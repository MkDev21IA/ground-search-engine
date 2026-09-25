from __future__ import annotations

import asyncio
from datetime import datetime
import json
import os
import time
from typing import Any, AsyncIterator
from urllib.parse import urlparse

from fastapi import APIRouter, Header, HTTPException, Query as FastQuery, Request
from fastapi.responses import StreamingResponse

from search_proxy.adapters.searxng import SearxngAdapter
from search_proxy.extractor import ContentExtractor
from search_proxy.models import Query, Result
from search_proxy.synthesis import (
    LLMClient,
    LLMConfig,
    SynthesisService,
    extract_citations,
)
from search_proxy.synthesis.builder import build_context
from search_proxy.synthesis.prompts import build_synthesis_messages
from .schemas import (
    CitationItem,
    ExtractedDocItem,
    HealthResponse,
    LatencyBreakdown,
    ModelPricingItem,
    ModelsResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    Telemetry,
    TokenUsage,
)

router = APIRouter(prefix="/api", tags=["search-engine"])

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


def get_effective_llm_config(
    x_llm_api_key: str | None = None,
    x_llm_base_url: str | None = None,
    x_llm_model: str | None = None,
    body_override: SearchRequest | None = None,
) -> LLMConfig:
    """Resolves LLMConfig with precedence: request body > HTTP headers > server .env."""
    base_url = (
        (body_override and body_override.base_url)
        or x_llm_base_url
        or os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    )
    api_key = (
        (body_override and body_override.api_key)
        or x_llm_api_key
        or os.getenv("LLM_API_KEY", "")
    )
    model = (
        (body_override and body_override.model)
        or x_llm_model
        or os.getenv("LLM_MODEL", "meta-llama/llama-3.2-3b-instruct")
    )
    return LLMConfig(base_url=base_url, api_key=api_key, model=model)


def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Checks the availability of the local SearXNG instance and configured model."""
    adapter = SearxngAdapter()
    searxng_connected = False
    try:
        results = adapter.search(Query(text="ping", max_results=1))
        searxng_connected = len(results) > 0 and not results[0].url.startswith("error:")
    except Exception:
        searxng_connected = False

    default_model = os.getenv("LLM_MODEL", "meta-llama/llama-3.2-3b-instruct")
    status = "ok" if searxng_connected else "degraded"
    return HealthResponse(
        status=status,
        searxng_connected=searxng_connected,
        searxng_url=adapter.base_url,
        default_model=default_model,
        version="0.1.0",
    )


@router.get("/models", response_model=ModelsResponse)
def get_models() -> ModelsResponse:
    """Returns recommended models and their pricing structures."""
    default_model = os.getenv("LLM_MODEL", "meta-llama/llama-3.2-3b-instruct")
    recommended = [
        "meta-llama/llama-3.2-3b-instruct",
        "qwen/qwen-2.5-7b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "deepseek/deepseek-chat",
        "google/gemini-2.5-flash",
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku",
    ]
    pricing_list = [
        ModelPricingItem(
            model=k,
            input_per_m=v["input_per_m"],
            output_per_m=v["output_per_m"],
        )
        for k, v in MODEL_PRICING.items()
    ]
    return ModelsResponse(
        default_model=default_model,
        recommended_models=recommended,
        pricing=pricing_list,
    )


@router.post("/search", response_model=SearchResponse)
async def search_sync(
    request: SearchRequest,
    x_llm_api_key: str | None = Header(None),
    x_llm_base_url: str | None = Header(None),
    x_llm_model: str | None = Header(None),
) -> SearchResponse:
    """Executes end-to-end grounded search synchronously."""
    t_start = time.time()
    config = get_effective_llm_config(
        x_llm_api_key=x_llm_api_key,
        x_llm_base_url=x_llm_base_url,
        x_llm_model=x_llm_model,
        body_override=request,
    )

    adapter = SearxngAdapter()
    extractor = ContentExtractor(timeout=10.0)
    llm_client = LLMClient(config=config)
    synthesis_svc = SynthesisService(llm_client=llm_client)

    # 1. Search
    t_search_start = time.time()
    query_obj = Query(text=request.query, lang=request.lang, max_results=request.max_results)
    results = await asyncio.to_thread(adapter.search, query_obj)
    search_duration_ms = int((time.time() - t_search_start) * 1000)

    # 2. Extract
    t_extract_start = time.time()
    valid_urls = [r.url for r in results if r.url and not r.url.startswith("error:")]
    extracted_docs = await asyncio.to_thread(extractor.extract_many, valid_urls)
    extract_duration_ms = int((time.time() - t_extract_start) * 1000)

    # 3. Synthesize
    t_syn_start = time.time()
    try:
        synthesis_output = await asyncio.to_thread(
            synthesis_svc.synthesize,
            query=request.query,
            results=results,
            extracted_docs=extracted_docs,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM synthesis failed: {exc}")
    synthesis_duration_ms = int((time.time() - t_syn_start) * 1000)
    total_duration_ms = int((time.time() - t_start) * 1000)

    p_tok = synthesis_output.raw_usage.get("prompt_tokens", 0)
    c_tok = synthesis_output.raw_usage.get("completion_tokens", 0)
    t_tok = synthesis_output.raw_usage.get("total_tokens", 0)
    cost = float(synthesis_output.raw_usage.get("cost") or estimate_cost(config.model, p_tok, c_tok))

    sources_items = [
        SearchResultItem(
            title=r.title,
            url=r.url,
            snippet=r.snippet,
            domain=extract_domain(r.url),
        )
        for r in results
        if r.url and not r.url.startswith("error:")
    ]

    extracted_items = [
        ExtractedDocItem(
            url=d.url,
            status=d.status,
            title=d.title or "",
            word_count=len(d.text.split()) if d.text else 0,
        )
        for d in extracted_docs
    ]

    citation_items = [
        CitationItem(label=c.label, url=c.url)
        for c in synthesis_output.citations
    ]

    telemetry = Telemetry(
        latencies=LatencyBreakdown(
            search_ms=search_duration_ms,
            extract_ms=extract_duration_ms,
            synthesis_ms=synthesis_duration_ms,
            total_ms=total_duration_ms,
        ),
        tokens=TokenUsage(
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            total_tokens=t_tok,
        ),
        cost_usd=round(cost, 6),
        model=config.model,
    )

    return SearchResponse(
        query=request.query,
        answer=synthesis_output.answer,
        citations=citation_items,
        sources=sources_items,
        extracted_docs=extracted_items,
        telemetry=telemetry,
    )


@router.get("/search/stream")
async def search_stream(
    q: str = FastQuery(..., min_length=1, description="Natural language search query"),
    lang: str = FastQuery("en", description="Search language code"),
    max_results: int = FastQuery(10, ge=1, le=20),
    x_llm_api_key: str | None = Header(None),
    x_llm_base_url: str | None = Header(None),
    x_llm_model: str | None = Header(None),
) -> StreamingResponse:
    """Executes grounded search with Server-Sent Events (SSE) streaming updates."""
    config = get_effective_llm_config(
        x_llm_api_key=x_llm_api_key,
        x_llm_base_url=x_llm_base_url,
        x_llm_model=x_llm_model,
    )

    adapter = SearxngAdapter()
    extractor = ContentExtractor(timeout=10.0)
    llm_client = LLMClient(config=config)

    async def sse_generator() -> AsyncIterator[str]:
        t_start = time.time()
        yield f"event: status\ndata: {json.dumps({'stage': 'search', 'message': 'Searching SearXNG...'})}\n\n"

        # 1. Search
        t_search = time.time()
        try:
            results = await asyncio.to_thread(adapter.search, Query(text=q, lang=lang, max_results=max_results))
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'error': f'Search failed: {exc}'})}\n\n"
            return
        search_ms = int((time.time() - t_search) * 1000)

        sources_payload = [
            {"title": r.title, "url": r.url, "snippet": r.snippet, "domain": extract_domain(r.url)}
            for r in results
            if r.url and not r.url.startswith("error:")
        ]
        yield f"event: search_results\ndata: {json.dumps(sources_payload)}\n\n"

        # 2. Extract
        yield f"event: status\ndata: {json.dumps({'stage': 'extract', 'message': f'Extracting content from {len(sources_payload)} web sources...'})}\n\n"
        t_extract = time.time()
        valid_urls = [s["url"] for s in sources_payload]
        extracted_docs = await asyncio.to_thread(extractor.extract_many, valid_urls)
        extract_ms = int((time.time() - t_extract) * 1000)

        ok_count = sum(1 for d in extracted_docs if d.status == "ok" and d.text)
        yield f"event: extraction_complete\ndata: {json.dumps({'total': len(extracted_docs), 'successful': ok_count})}\n\n"

        # 3. Synthesis Preparation
        yield f"event: status\ndata: {json.dumps({'stage': 'synthesis', 'message': f'Synthesizing verified grounded answer using {config.model}...'})}\n\n"
        context_str, _ = build_context(results=results, extracted_docs=extracted_docs)
        messages = build_synthesis_messages(query=q, context=context_str)

        # 4. Stream Tokens
        t_syn = time.time()
        full_text = []
        usage_data: dict[str, Any] = {}

        try:
            def sync_stream_tokens():
                return list(llm_client.stream_generate(messages))

            # Fetch token stream (or stream chunks asynchronously)
            stream_chunks = await asyncio.to_thread(sync_stream_tokens)

            for chunk in stream_chunks:
                if chunk["type"] == "token":
                    token = chunk["content"]
                    full_text.append(token)
                    yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"
                elif chunk["type"] == "usage":
                    usage_data = chunk["usage"]

        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'error': f'Synthesis failed: {exc}'})}\n\n"
            return

        synthesis_ms = int((time.time() - t_syn) * 1000)
        total_ms = int((time.time() - t_start) * 1000)

        complete_answer = "".join(full_text)
        citations = extract_citations(complete_answer)
        citations_payload = [{"label": c.label, "url": c.url} for c in citations]
        yield f"event: citations\ndata: {json.dumps(citations_payload)}\n\n"

        # 5. Telemetry
        p_tok = usage_data.get("prompt_tokens", 0)
        c_tok = usage_data.get("completion_tokens", len(complete_answer.split()))
        t_tok = usage_data.get("total_tokens", p_tok + c_tok)
        cost = float(usage_data.get("cost") or estimate_cost(config.model, p_tok, c_tok))

        telemetry_payload = {
            "latencies": {
                "search_ms": search_ms,
                "extract_ms": extract_ms,
                "synthesis_ms": synthesis_ms,
                "total_ms": total_ms,
            },
            "tokens": {"prompt_tokens": p_tok, "completion_tokens": c_tok, "total_tokens": t_tok},
            "cost_usd": round(cost, 6),
            "model": config.model,
        }
        yield f"event: telemetry\ndata: {json.dumps(telemetry_payload)}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
