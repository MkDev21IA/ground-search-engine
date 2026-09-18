# 0012 — Head-to-Head Evaluation and Cost-Effectiveness Benchmark (Week of Sep 21–25, 2026)

**Status:** Accepted  
**Date:** 2026-09-18  

## Context

The core pipeline of `ground-search-engine` — canonical search via SearXNG ([0006](0006-search-evaluation-methodology.md)), ethical HTML and PDF extraction with graceful degradation ([0009](0009-source-content-extraction.md)), and grounded synthesis with mandatory inline citations ([0011](0011-pipeline-validation-with-commercial-model.md)) — is fully implemented with 100% offline unit test coverage (20/20 passed).

Before committing engineering resources to frontend design and FastAPI application packaging, a fundamental product hypothesis must be empirically verified:
> *Does `ground-search-engine` demonstrably outperform direct commercial LLM chat (without search) in factual precision, citation verifiability, temporal accuracy, and cost-effectiveness?*

Following the foundational philosophy of measuring before building (`AGENTS.md`), establishing concrete benchmarks and cost calculations ($/query compared to commercial $20/month SaaS platforms like Perplexity Pro or ChatGPT Plus) is required to position the project compellingly for open-source dissemination and potential downstream commercialization.

## Decision

Dedicate the work sprint of **September 21 to September 25, 2026** (in daily 30-minute focused blocks) to an empirical **Head-to-Head Comparative Benchmark** and subsequent productization:

### 1. Evaluation Modalities & Model Matrix

The benchmark will compare two execution modes across the test prompt suite ([`prompts/prompts_v1.yaml`](../prompts/prompts_v1.yaml)):
- **Mode A (Direct Raw Chat)**: User prompt sent directly to the LLM without external search context or retrieval.
- **Mode B (Ground Search Engine Pipeline)**: Full pipeline execution (SearXNG live search + Trafilatura/PyPDF extraction + snippet fallback + grounded synthesis with mandatory `[Title](URL)` citations).

**Evaluated Models:**
1. `gemini-2.5-flash` (Google AI Studio via OpenAI-compatible endpoint): Primary workhorse for high speed and ultra-low token cost ($0.075 / 1M input tokens).
2. `gpt-4o-mini` (OpenAI): Secondary commercial benchmark reference.
3. `qwen2.5-7b-instruct` / `qwen2.5-14b-instruct` (Local via Ollama/LM Studio): Sovereign, zero-cost, 100% offline baseline per [0003](0003-llm-model-architecture.md).

### 2. Evaluated Metrics

1. **Attribution & Citation Density**: Number of verified primary/secondary citations inline per factual claim (0 in raw chat vs. N in pipeline).
2. **Temporal Freshness & Hallucination Resistance**: Factual accuracy on recent events (2025/2026 developments, regional statistics) where raw models typically hallucinate or report knowledge cutoff.
3. **Controversy Balance**: Objective representation of divergent perspectives with citations on contested topics (clinical studies, historiography).
4. **Token Economics & Unit Cost**: Exact measurement of prompt tokens, completion tokens, and calculated USD cost per search vs. fixed $20/month SaaS subscriptions.
5. **End-to-End Latency**: Total execution time (search + extraction + LLM inference) vs. raw chat latency.

### 3. Sprint Roadmap (Sep 21 – Sep 25, 2026 / 30 min daily)

| Day | Focus | Primary Objective | Deliverable |
| :--- | :--- | :--- | :--- |
| **Monday (21/09)** | **A/B Benchmark Harness** | Implement `search-proxy/scripts/run_head_to_head_eval.py` running prompts in Mode A and Mode B side-by-side. | Script generating dual structured JSON records with tokens, latencies, and costs. |
| **Tuesday (22/09)** | **Benchmark Execution** | Execute comparative runs across `gemini-2.5-flash` and compile metrics table. | Quantitative comparison report with cost calculations ($/query) and token usage. |
| **Wednesday (23/09)** | **Factual Audit & Verdict** | Qualitative audit of critical queries (fusion 2026, energy statistics, clinical trials). Formulate go/no-go product decision. | Impact analysis report documenting verified superiority over raw chat. |
| **Thursday (24/09)** | **FastAPI Core & Telemetry** | Build FastAPI backend service exposing `/api/search` with SSE streaming and real-time cost/token telemetry. | Working API service verifiable via `curl` and OpenAPI docs. |
| **Friday (25/09)** | **Showcase Web UI** | Create clean web interface (HTML5 + Tailwind CSS) with search input, BYOK key modal, and verified source cards. | Functional local web application accessible at `http://localhost:8000`. |

## Consequences

- **Evidence-Based Engineering**: Prevents building unnecessary features before proving superior value.
- **Compelling Positioning**: Delivers ready-to-publish evidence ("99.6% cheaper than Perplexity with zero temporal hallucinations") for public release.
- **Architectural Readiness**: Integrates token and cost telemetry directly into the upcoming API design.
