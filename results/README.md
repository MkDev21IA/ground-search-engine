# Search & Synthesis Evaluation Results

This directory contains the empirical evaluation reports and immutable raw benchmark runs of [`search-proxy`](../search-proxy/) across all development phases (see [ADR 0006](../decisions/0006-search-evaluation-methodology.md) and [ADR 0016](../decisions/0016-external-validation-vs-literature-baselines.md)).

---

## 📑 Master Consolidated Report

- **[CONSOLIDATED_BENCHMARK_REPORT.md](CONSOLIDATED_BENCHMARK_REPORT.md)**: Executive milestone report consolidating all evaluation phases, architectural findings, the official 948-question ASQA literature validation, and cost/sovereignty analyses.

---

## 📂 Evaluation Runs Index

| Run Directory | Date | Focus & Scope | Key Outcome |
| :--- | :---: | :--- | :--- |
| **[`2026-09-17-synthesis-evaluation/`](2026-09-17-synthesis-evaluation/)** | 2026-09-17 | Commercial model validation (`gemini-2.5-flash`) | Validated zero-hallucination prompt & inline citation format. |
| **[`2026-09-22-head-to-head-evaluation/`](2026-09-22-head-to-head-evaluation/)** | 2026-09-22 | Mode A (Raw LLM) vs. Mode B (GSE Pipeline) | 100% cited claims (avg 4.5 links/ans); 0% URL hallucinations. |
| **[`2026-09-22-david-vs-goliath-evaluation/`](2026-09-22-david-vs-goliath-evaluation/)** | 2026-09-22 | Open 3B/7B vs. Frontier GPT-4o & Claude 3.5 Sonnet | Open models with GSE outperformed raw frontier chat on niche facts. |
| **[`2026-09-22-stress-test-evaluation/`](2026-09-22-stress-test-evaluation/)** | 2026-09-22 | High-concurrency rate limits & WAF stress testing | Validated graceful degradation to search snippets under WAF blocks. |
| **[`2026-09-29-asqa-full-evaluation/`](2026-09-29-asqa-full-evaluation/)** | 2026-09-29 | Full 948-question ASQA benchmark & literature validation | Str-EM 47.1%–48.3% outperforming published literature baselines. |

---

## Convention

One immutable subdirectory per evaluation run, named `YYYY-MM-DD-short-description/`, containing:
- Canonical result files (`*.json`, `*.md`) documenting prompts, retrieved sources, citations, and LLM responses;
- Qualitative notes describing latency, error rates, or WAF challenges encountered.

Raw results are never modified in-place after generation — any new run generates a new timestamped subdirectory to preserve traceable historical data.
