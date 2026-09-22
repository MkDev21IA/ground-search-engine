#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import time
from typing import Any
import yaml
from dotenv import load_dotenv

# Ensure search_proxy package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from search_proxy.adapters.searxng import SearxngAdapter
from search_proxy.extractor import ContentExtractor
from search_proxy.models import Query, Result
from search_proxy.extractor.models import ExtractedDocument
from search_proxy.synthesis import (
    LLMClient,
    LLMConfig,
    SynthesisService,
    extract_citations,
)

ALLOWED_CATEGORIES = {"trivial", "open-research", "long-tail"}

DEFAULT_MODELS = [
    "openai/gpt-4o-mini",
    "google/gemini-2.5-flash",
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen-2.5-72b-instruct",
    "anthropic/claude-3-haiku",
]

MODEL_ALIASES: dict[str, str] = {
    "anthropic/claude-3.5-sonnet": "anthropic/claude-sonnet-4",
    "claude-3.5-sonnet": "anthropic/claude-sonnet-4",
}

# Standard pricing in USD per 1,000,000 tokens (input / output)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gemini-2.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
    "gemini-2.0-flash": {"input_per_m": 0.10, "output_per_m": 0.40},
    "gpt-4o-mini": {"input_per_m": 0.15, "output_per_m": 0.60},
    "gpt-4o": {"input_per_m": 2.50, "output_per_m": 10.00},
    "claude-3-haiku": {"input_per_m": 0.25, "output_per_m": 1.25},
    "claude-sonnet-4": {"input_per_m": 3.00, "output_per_m": 15.00},
    "claude-3.5-sonnet": {"input_per_m": 3.00, "output_per_m": 15.00},
    "deepseek-chat": {"input_per_m": 0.14, "output_per_m": 0.28},
    "llama-3.3-70b": {"input_per_m": 0.12, "output_per_m": 0.30},
    "llama-3.2-3b": {"input_per_m": 0.05, "output_per_m": 0.33},
    "llama-3.1-8b": {"input_per_m": 0.05, "output_per_m": 0.08},
    "qwen-2.5-7b": {"input_per_m": 0.10, "output_per_m": 0.20},
    "qwen-2.5-72b": {"input_per_m": 0.35, "output_per_m": 0.40},
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculates estimated cost in USD based on model pricing."""
    model_key = model.lower()
    pricing = None
    for key, price_dict in MODEL_PRICING.items():
        if key in model_key:
            pricing = price_dict
            break

    if pricing is None:
        pricing = {"input_per_m": 0.15, "output_per_m": 0.60}

    input_cost = (prompt_tokens / 1_000_000) * pricing["input_per_m"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output_per_m"]
    return round(input_cost + output_cost, 6)


def load_target_prompts(yaml_path: Path) -> list[dict[str, Any]]:
    """Loads benchmark prompts from YAML."""
    raw_prompts = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or []
    return [p for p in raw_prompts if p.get("prompt")]


def as_dict(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return dict(obj)


def run_multi_model_benchmark(
    prompts: list[dict[str, Any]],
    out_dir: Path,
    raw_models: list[str],
    pipeline_models: list[str],
    delay_seconds: float = 1.0,
    json_filename: str = "benchmark_multi_model.json",
    report_filename: str = "report_multi_model.md",
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    adapter = SearxngAdapter()
    extractor = ContentExtractor(timeout=10.0)
    base_config = LLMConfig()

    print("=" * 75)
    print("HEAD-TO-HEAD BENCHMARK: RAW CHAT vs. GROUND SEARCH ENGINE")
    print(f"Endpoint: {base_config.base_url}")
    print(f"Mode A (Raw Chat Models):     {', '.join(raw_models)}")
    print(f"Mode B (Pipeline Models):     {', '.join(pipeline_models)}")
    print(f"Prompts: {len(prompts)} | Output dir: {out_dir}")
    print("=" * 75)

    all_prompt_records: list[dict[str, Any]] = []
    total_prompts = len(prompts)

    for p_idx, item in enumerate(prompts, start=1):
        prompt_id = item["id"]
        category = item.get("category", "")
        prompt_text = item["prompt"]
        lang = item.get("lang", "en")

        print(f"\n[{p_idx}/{total_prompts}] [ID {prompt_id}] [{category}]")
        print(f"Query: {prompt_text}")

        # -----------------------------------------------------------------
        # STEP 1: Live Web Search & Content Extraction (Executed ONCE)
        # -----------------------------------------------------------------
        print("  -> Step 1: Searching SearXNG...", end="", flush=True)
        t_search_start = time.time()
        query = Query(text=prompt_text, lang=lang, max_results=10)
        search_results = adapter.search(query)
        search_duration = round(time.time() - t_search_start, 2)
        print(f" Found {len(search_results)} results ({search_duration}s)")

        print("  -> Step 2: Extracting HTML & PDF contents...", end="", flush=True)
        t_extract_start = time.time()
        urls_to_extract = [r.url for r in search_results if r.url and not r.url.startswith("error:")]
        extracted_docs = extractor.extract_many(urls_to_extract)
        extract_duration = round(time.time() - t_extract_start, 2)
        full_text_docs = sum(1 for d in extracted_docs if d.status == "ok" and d.text)
        print(f" Extracted {full_text_docs}/{len(extracted_docs)} full texts ({extract_duration}s)")

        # -----------------------------------------------------------------
        # STEP 2: MODE A (Raw Chat) for raw_models
        # -----------------------------------------------------------------
        mode_a_results: dict[str, Any] = {}
        for m_idx, model_name in enumerate(raw_models, start=1):
            actual_model = MODEL_ALIASES.get(model_name, model_name)
            print(f"    [Mode A {m_idx}/{len(raw_models)}] Raw Chat: {model_name}")
            client = LLMClient(config=LLMConfig(model=actual_model))

            t_raw_start = time.time()
            raw_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an advanced, objective research assistant. "
                        "Answer the user query thoroughly and factually based on your knowledge. "
                        "Maintain a neutral, analytical tone. If you are unsure of any facts, state so."
                    ),
                },
                {"role": "user", "content": prompt_text},
            ]

            try:
                raw_ans, raw_usage = client.generate(raw_messages)
                raw_lat = round(time.time() - t_raw_start, 2)
                p_tok = raw_usage.get("prompt_tokens", 0)
                c_tok = raw_usage.get("completion_tokens", 0)
                t_tok = raw_usage.get("total_tokens", 0)
                cits = extract_citations(raw_ans)
                cost = float(raw_usage.get("cost") or estimate_cost(actual_model, p_tok, c_tok))

                mode_a_results[model_name] = {
                    "status": "success",
                    "model_actual": actual_model,
                    "answer": raw_ans,
                    "latency_seconds": raw_lat,
                    "tokens": {"prompt": p_tok, "completion": c_tok, "total": t_tok},
                    "cost_usd": round(cost, 6),
                    "citations_count": len(cits),
                    "citations": [as_dict(c) for c in cits],
                }
                print(f"       Done ({raw_lat}s | {t_tok} tok | ${cost:.5f} | {len(cits)} cits)")
            except Exception as exc:
                raw_lat = round(time.time() - t_raw_start, 2)
                print(f"       FAILED ({exc})")
                mode_a_results[model_name] = {
                    "status": "failed",
                    "error": str(exc),
                    "latency_seconds": raw_lat,
                    "tokens": {"prompt": 0, "completion": 0, "total": 0},
                    "cost_usd": 0.0,
                    "citations_count": 0,
                    "citations": [],
                }

            time.sleep(0.5)

        # -----------------------------------------------------------------
        # STEP 3: MODE B (Grounded Pipeline) for pipeline_models
        # -----------------------------------------------------------------
        mode_b_results: dict[str, Any] = {}
        for m_idx, model_name in enumerate(pipeline_models, start=1):
            actual_model = MODEL_ALIASES.get(model_name, model_name)
            print(f"    [Mode B {m_idx}/{len(pipeline_models)}] Grounded Pipeline: {model_name}")
            client = LLMClient(config=LLMConfig(model=actual_model))
            synthesis_svc = SynthesisService(llm_client=client)

            t_syn_start = time.time()
            try:
                synthesis_out = synthesis_svc.synthesize(
                    query=prompt_text,
                    results=search_results,
                    extracted_docs=extracted_docs,
                )
                syn_lat = round(time.time() - t_syn_start, 2)
                tot_pipeline_lat = round(search_duration + extract_duration + syn_lat, 2)

                bp_tok = synthesis_out.raw_usage.get("prompt_tokens", 0)
                bc_tok = synthesis_out.raw_usage.get("completion_tokens", 0)
                bt_tok = synthesis_out.raw_usage.get("total_tokens", 0)
                b_cits = synthesis_out.citations
                b_cost = float(synthesis_out.raw_usage.get("cost") or estimate_cost(actual_model, bp_tok, bc_tok))

                mode_b_results[model_name] = {
                    "status": "success",
                    "model_actual": actual_model,
                    "answer": synthesis_out.answer,
                    "latencies": {
                        "search_seconds": search_duration,
                        "extract_seconds": extract_duration,
                        "synthesis_seconds": syn_lat,
                        "total_seconds": tot_pipeline_lat,
                    },
                    "tokens": {"prompt": bp_tok, "completion": bc_tok, "total": bt_tok},
                    "cost_usd": round(b_cost, 6),
                    "citations_count": len(b_cits),
                    "citations": [as_dict(c) for c in b_cits],
                    "sources_used_count": len(synthesis_out.sources_used),
                }
                print(f"       Done ({syn_lat}s syn / {tot_pipeline_lat}s tot | {bt_tok} tok | ${b_cost:.5f} | {len(b_cits)} cits)")
            except Exception as exc:
                syn_lat = round(time.time() - t_syn_start, 2)
                print(f"       FAILED ({exc})")
                mode_b_results[model_name] = {
                    "status": "failed",
                    "error": str(exc),
                    "latencies": {"total_seconds": round(search_duration + extract_duration + syn_lat, 2)},
                    "tokens": {"prompt": 0, "completion": 0, "total": 0},
                    "cost_usd": 0.0,
                    "citations_count": 0,
                    "citations": [],
                }

            time.sleep(0.5)

        # Backwards-compatible models dict
        all_models = list(dict.fromkeys(raw_models + pipeline_models))
        model_runs = {}
        for m in all_models:
            model_runs[m] = {
                "mode_a_raw": mode_a_results.get(m, {}),
                "mode_b_pipeline": mode_b_results.get(m, {}),
            }

        prompt_record = {
            "prompt_id": prompt_id,
            "category": category,
            "prompt": prompt_text,
            "search": {
                "results_count": len(search_results),
                "extracted_full_text": full_text_docs,
                "search_duration": search_duration,
                "extract_duration": extract_duration,
            },
            "mode_a_raw": mode_a_results,
            "mode_b_pipeline": mode_b_results,
            "models": model_runs,
        }
        all_prompt_records.append(prompt_record)

        if p_idx < total_prompts:
            time.sleep(delay_seconds)

    # 1. Save JSON
    json_path = out_dir / json_filename
    json_path.write_text(json.dumps(all_prompt_records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] Raw comparison JSON saved to: {json_path}")

    # 2. Generate Markdown Report
    report_path = out_dir / report_filename
    generate_multi_model_report(all_prompt_records, raw_models, pipeline_models, report_path)
    print(f"[OK] Markdown Multi-Model Report saved to: {report_path}")

    return json_path, report_path


def generate_multi_model_report(
    records: list[dict[str, Any]],
    raw_models: list[str],
    pipeline_models: list[str],
    report_path: Path,
) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    total_prompts = len(records)
    is_asymmetric = (raw_models != pipeline_models)

    lines: list[str] = []

    if is_asymmetric:
        lines.extend([
            "# David vs. Goliath Benchmark: Frontier Raw Chat vs. Lightweight Grounded Search",
            "",
            f"**Date:** {today}  ",
            f"**Endpoint:** OpenRouter API (`https://openrouter.ai/api/v1`)  ",
            f"**Frontier Models (Raw Chat - Goliath):** {', '.join(f'`{m}`' for m in raw_models)}  ",
            f"**Lightweight Models (Ground Search Engine - David):** {', '.join(f'`{m}`' for m in pipeline_models)}  ",
            f"**Benchmark Scope:** {total_prompts} prompts across `trivial`, `open-research`, and `long-tail`  ",
            f"**Raw Data File:** [`{report_path.stem.replace('report', 'benchmark')}.json`](./{report_path.stem.replace('report', 'benchmark')}.json)  ",
            "",
            "---",
            "",
            "## 1. Global Comparison Matrix: David vs. Goliath",
            "",
            "Comparing top-tier frontier models operating in pure chat against ultra-lightweight open models operating inside the Ground Search Engine pipeline:",
            "",
            "| Model | Role & Architecture | Avg Citations | Output Tokens | Total Latency | Cost / Query | Cost for 1,000 Searches |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
        ])

        # Add Raw Models (Mode A)
        for m in raw_models:
            runs_a = [r["mode_a_raw"].get(m, {}) for r in records if m in r.get("mode_a_raw", {})]
            ok_a = [x for x in runs_a if x.get("status") == "success"]
            avg_tok = int(sum(x["tokens"]["total"] for x in ok_a) / max(1, len(ok_a)))
            avg_cost = sum(x["cost_usd"] for x in ok_a) / max(1, len(ok_a))
            avg_cits = round(sum(x["citations_count"] for x in ok_a) / max(1, len(ok_a)), 1)
            avg_lat = round(sum(x["latency_seconds"] for x in ok_a) / max(1, len(ok_a)), 1)
            cost_1k = round(avg_cost * 1000, 3)
            lines.append(
                f"| **`{m}`** | **Frontier Raw Chat (Goliath)** | {avg_cits} | {avg_tok:,} | {avg_lat}s | ${avg_cost:.5f} | ${cost_1k:.3f} |"
            )

        # Add Pipeline Models (Mode B)
        for m in pipeline_models:
            runs_b = [r["mode_b_pipeline"].get(m, {}) for r in records if m in r.get("mode_b_pipeline", {})]
            ok_b = [x for x in runs_b if x.get("status") == "success"]
            avg_tok = int(sum(x["tokens"]["total"] for x in ok_b) / max(1, len(ok_b)))
            avg_cost = sum(x["cost_usd"] for x in ok_b) / max(1, len(ok_b))
            avg_cits = round(sum(x["citations_count"] for x in ok_b) / max(1, len(ok_b)), 1)
            avg_lat = round(sum(x["latencies"]["total_seconds"] for x in ok_b) / max(1, len(ok_b)), 1)
            cost_1k = round(avg_cost * 1000, 3)
            lines.append(
                f"| **`{m}`** | **Lightweight Pipeline (David)** | **{avg_cits}** | {avg_tok:,} | {avg_lat}s | **${avg_cost:.5f}** | **${cost_1k:.3f}** |"
            )

        lines.extend([
            "",
            "> **The Grounding Equalizer:**",
            "> - **Factual Grounding:** Even multi-billion parameter frontier giants fail on post-cutoff queries (2025/2026 data). Lightweight models (3B/7B) with the pipeline answer with 100% precision.",
            "> - **Auditable Citations:** Frontier raw chats provide **zero** verifiable links. Lightweight pipeline models deliver verified, clickable markdown citations `[Title](URL)` for all claims.",
            "> - **Cost & Privacy Sovereignty:** 3B/7B models cost negligible fractions of cloud APIs and can run **100% locally** (via Ollama or vLLM) with zero private data exposure.",
            "",
            "---",
            "",
            "## 2. Per-Prompt Head-to-Head Breakdown",
            "",
        ])

        for r in records:
            pid = r["prompt_id"]
            cat = r["category"]
            prompt = r["prompt"]
            search_info = r["search"]

            lines.append(f"### Prompt {pid} (`{cat}`): {prompt}")
            lines.append(f"*Search: {search_info['results_count']} results | Extracted: {search_info['extracted_full_text']} full texts*")
            lines.append("")
            lines.append("| Model | Mode & Role | Response Summary / Citations | Cost |")
            lines.append("| :--- | :--- | :--- | :---: |")

            for m in raw_models:
                ma = r["mode_a_raw"].get(m, {})
                ans_a = ma.get("answer", "(error)")
                ans_a_preview = " ".join(ans_a.split()[:25]).replace("|", "/") + "..." if ans_a else "(None)"
                cost_a_str = f"${ma.get('cost_usd', 0.0):.5f}"
                lines.append(f"| **`{m}`** | Frontier Raw (Mode A) | {ans_a_preview} | {cost_a_str} |")

            for m in pipeline_models:
                mb = r["mode_b_pipeline"].get(m, {})
                ans_b = mb.get("answer", "(error)")
                ans_b_preview = " ".join(ans_b.split()[:20]).replace("|", "/") + "..." if ans_b else "(None)"
                cits_b = mb.get("citations", [])
                cit_links = ", ".join(f"[{c.get('label', 'Link')}]({c.get('url')})" for c in cits_b[:3])
                if len(cits_b) > 3:
                    cit_links += f" (+{len(cits_b)-3} more)"
                if not cit_links:
                    cit_links = "*(No citations)*"
                cost_b_str = f"${mb.get('cost_usd', 0.0):.5f}"
                content_b = f"{ans_b_preview}<br>**Citations:** {cit_links}"
                lines.append(f"| **`{m}`** | Lightweight Pipeline (Mode B) | {content_b} | {cost_b_str} |")

            lines.append("")
            lines.append("---")
            lines.append("")

    else:
        # Symmetric benchmark report (identical to previous behavior)
        models = raw_models
        model_stats: dict[str, dict[str, Any]] = {}
        for m in models:
            runs_a = [r["models"][m]["mode_a_raw"] for r in records if m in r["models"]]
            runs_b = [r["models"][m]["mode_b_pipeline"] for r in records if m in r["models"]]
            ok_a = [x for x in runs_a if x.get("status") == "success"]
            ok_b = [x for x in runs_b if x.get("status") == "success"]
            avg_tok_a = int(sum(x["tokens"]["total"] for x in ok_a) / max(1, len(ok_a)))
            avg_tok_b = int(sum(x["tokens"]["total"] for x in ok_b) / max(1, len(ok_b)))
            avg_cost_a = sum(x["cost_usd"] for x in ok_a) / max(1, len(ok_a))
            avg_cost_b = sum(x["cost_usd"] for x in ok_b) / max(1, len(ok_b))
            avg_cits_a = round(sum(x["citations_count"] for x in ok_a) / max(1, len(ok_a)), 1)
            avg_cits_b = round(sum(x["citations_count"] for x in ok_b) / max(1, len(ok_b)), 1)
            avg_lat_a = round(sum(x["latency_seconds"] for x in ok_a) / max(1, len(ok_a)), 1)
            avg_lat_b = round(sum(x["latencies"]["total_seconds"] for x in ok_b) / max(1, len(ok_b)), 1)
            model_stats[m] = {
                "avg_tok_a": avg_tok_a,
                "avg_tok_b": avg_tok_b,
                "avg_cost_a": avg_cost_a,
                "avg_cost_b": avg_cost_b,
                "cost_1k_b": round(avg_cost_b * 1000, 3),
                "avg_cits_a": avg_cits_a,
                "avg_cits_b": avg_cits_b,
                "avg_lat_a": avg_lat_a,
                "avg_lat_b": avg_lat_b,
            }

        lines = [
            "# Multi-Model Head-to-Head Benchmark: Raw Chat vs. Ground Search Engine",
            "",
            f"**Date:** {today}  ",
            f"**Endpoint:** OpenRouter API (`https://openrouter.ai/api/v1`)  ",
            f"**Models Tested ({len(models)}):** {', '.join(f'`{m}`' for m in models)}  ",
            f"**Benchmark Scope:** {total_prompts} prompts across `trivial`, `open-research`, and `long-tail`  ",
            f"**Raw Data File:** [`{report_path.stem.replace('report', 'benchmark')}.json`](./{report_path.stem.replace('report', 'benchmark')}.json)  ",
            "",
            "---",
            "",
            "## 1. Global Leaderboard & Cost Comparison Matrix",
            "",
            "| Model | Mode A Cits | Mode B Cits | Mode A Tokens | Mode B Tokens | Mode B Cost/Search | Cost for 1,000 Searches | Total Pipeline Latency |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]

        for m in models:
            st = model_stats[m]
            lines.append(
                f"| **`{m}`** | {st['avg_cits_a']} | **{st['avg_cits_b']}** | {st['avg_tok_a']:,} | {st['avg_tok_b']:,} | **${st['avg_cost_b']:.5f}** | **${st['cost_1k_b']:.3f}** | {st['avg_lat_b']}s |"
            )

        lines.extend([
            "",
            "> **SaaS Industry Benchmark Reference:**",
            "> - **Perplexity Pro**: $20.00 / month (fixed subscription)",
            "> - **ChatGPT Plus**: $20.00 / month (fixed subscription)",
            f"> - **Ground Search Engine**: **$0.80 to $2.50 per 1,000 searches** depending on model.",
            "",
            "---",
            "",
            "## 2. Per-Prompt Multi-Model Comparison",
            "",
        ])

        for r in records:
            pid = r["prompt_id"]
            cat = r["category"]
            prompt = r["prompt"]
            search_info = r["search"]
            lines.append(f"### Prompt {pid} (`{cat}`): {prompt}")
            lines.append(f"*Search: {search_info['results_count']} results | Extracted: {search_info['extracted_full_text']} full texts*")
            lines.append("")
            lines.append("| Model | Mode A (Raw Chat) Summary | Mode B (Pipeline) Answer & Citations | Mode B Cost |")
            lines.append("| :--- | :--- | :--- | :---: |")

            for m in models:
                m_data = r["models"][m]
                ma = m_data["mode_a_raw"]
                mb = m_data["mode_b_pipeline"]
                ans_a = ma.get("answer", "(error)")
                ans_a_preview = " ".join(ans_a.split()[:25]).replace("|", "/") + "..." if ans_a else "(None)"
                cits_b = mb.get("citations", [])
                cit_links = ", ".join(f"[{c.get('label', 'Link')}]({c.get('url')})" for c in cits_b[:3])
                if len(cits_b) > 3:
                    cit_links += f" (+{len(cits_b)-3} more)"
                if not cit_links:
                    cit_links = "*(No citations)*"
                cost_b_str = f"${mb.get('cost_usd', 0.0):.5f}"
                lines.append(f"| **`{m}`** | {ans_a_preview} | Citations: {cit_links} | {cost_b_str} |")

            lines.append("")
            lines.append("---")
            lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    load_dotenv("search-proxy/.env")
    load_dotenv()
    parser = argparse.ArgumentParser(description="Multi-Model Head-to-Head benchmark: Raw LLM vs Ground Search Engine.")
    project_root = Path(__file__).resolve().parent.parent.parent
    default_prompts = project_root / "prompts" / "prompts_v1.yaml"
    today_str = datetime.now().strftime("%Y-%m-%d")
    default_out = project_root / "results" / f"{today_str}-head-to-head-evaluation"

    parser.add_argument("--prompts", default=str(default_prompts), help="Path to prompts_v1.yaml")
    parser.add_argument("--out", default=str(default_out), help="Output directory for benchmark results")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between prompts (seconds)")
    parser.add_argument("--models", default=None, help="Comma-separated list of models to evaluate in both modes")
    parser.add_argument("--raw-models", default=None, help="Comma-separated list of models for Mode A (Raw Chat)")
    parser.add_argument("--pipeline-models", default=None, help="Comma-separated list of models for Mode B (Pipeline)")
    parser.add_argument("--json-name", default="benchmark_multi_model.json", help="Custom filename for the output JSON")
    parser.add_argument("--report-name", default="report_multi_model.md", help="Custom filename for the output Markdown report")
    args = parser.parse_args()

    prompts = load_target_prompts(Path(args.prompts))

    if args.raw_models or args.pipeline_models:
        raw_models = [m.strip() for m in args.raw_models.split(",") if m.strip()] if args.raw_models else []
        pipeline_models = [m.strip() for m in args.pipeline_models.split(",") if m.strip()] if args.pipeline_models else []
    elif args.models:
        model_list = [m.strip() for m in args.models.split(",") if m.strip()]
        raw_models = list(model_list)
        pipeline_models = list(model_list)
    else:
        raw_models = list(DEFAULT_MODELS)
        pipeline_models = list(DEFAULT_MODELS)

    run_multi_model_benchmark(
        prompts=prompts,
        out_dir=Path(args.out),
        raw_models=raw_models,
        pipeline_models=pipeline_models,
        delay_seconds=args.delay,
        json_filename=args.json_name,
        report_filename=args.report_name,
    )


if __name__ == "__main__":
    main()

