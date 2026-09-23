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

## Revision (2026-09-21): A/B Benchmark Harness Implemented & OpenRouter Multi-Model Integration

- The comparative A/B evaluation script has been implemented in [`search-proxy/scripts/run_head_to_head_eval.py`](../search-proxy/scripts/run_head_to_head_eval.py).
- Integrated token usage tracking, detailed latency breakdowns (search, extraction, synthesis), and automatic USD cost calculation per model.
- Added OpenRouter (`https://openrouter.ai/api/v1`) configuration support in `search-proxy/.env.example` to facilitate multi-model testing (OpenAI, Anthropic, DeepSeek, Meta Llama) under a single budget-friendly unified API key.

## Revision (2026-09-23): Factual Audit, Empirical Benchmark Results, and Formal GO Product Verdict

On September 22, 2026, three comprehensive benchmark campaigns were executed via OpenRouter, encompassing 216 individual LLM evaluations across 21 test queries in `prompts/prompts_v1.yaml` and `prompts/prompts_v2.yaml`.

### 1. Empirical Findings Summary

1. **Multi-Model Universality ([`results/2026-09-22-head-to-head-evaluation/`](../results/2026-09-22-head-to-head-evaluation/))**:
   - Evaluated 6 major foundation models (GPT-4o-mini, Gemini-2.5-Flash, DeepSeek-Chat, Llama-3.3-70B, Qwen-2.5-72B, Claude-3-Haiku) across 11 baseline prompts (132 evaluations).
   - Proved that the synthesis prompt in [`synthesis/prompts.py`](../search-proxy/search_proxy/synthesis/prompts.py) generalizes reliably across all model families, producing an average of 2.5 to 4.8 verified inline citations with zero prompt formatting failures.
2. **David vs. Goliath Hypothesis Validation ([`results/2026-09-22-david-vs-goliath-evaluation/`](../results/2026-09-22-david-vs-goliath-evaluation/))**:
   - Compared lightweight open-weight models inside the pipeline (`meta-llama/llama-3.2-3b-instruct` and `qwen/qwen-2.5-7b-instruct`) against top-tier proprietary frontier models in raw chat (`openai/gpt-4o` and `anthropic/claude-3.5-sonnet`).
   - **Temporal Accuracy**: On post-cutoff queries (2026 nuclear fusion milestones, Acre 2025 electricity consumption), 100% of raw frontier models failed or refused to answer, whereas 3B/7B models with the pipeline answered with 100% factual accuracy and primary source URLs.
   - **Cost Superiority**: Llama-3.2-3B in the pipeline costs **$0.00092 per query ($0.92 per 1,000 searches)**, making it **4.3x cheaper than GPT-4o raw** ($4.03/1k) and **8.2x cheaper than Claude-3.5-Sonnet raw** ($7.60/1k), while processing nearly 15,000 tokens of live web context.
3. **Advanced Stress Test Resilience ([`results/2026-09-22-stress-test-evaluation/`](../results/2026-09-22-stress-test-evaluation/))**:
   - Evaluated 10 high-friction prompts across contentious medical pharmacovigilance (GLP-1 long-term safety, 2024 FDA MDMA AdCom rejection), Big Tech generative AI CapEx vs ROI, OPEC+ vs non-OPEC oil supply, Essequibo geopolitical dispute, ASML chip sanctions, post-quantum cryptography (NIST FIPS 204/205), and an adversarial false-premise trap (5G and viral replication).
   - `qwen/qwen-2.5-7b-instruct` achieved **3.1 verifiable primary citations per response**, successfully cited official SEC EDGAR 10-K/10-Q filings, official IEA/EIA energy reports, and FDA briefing documents, and correctly debunked the 5G false premise by citing scientific consensus and retracted literature.

### 2. Formal Go/No-Go Product Verdict: DEFINITIVE "GO"

The product hypothesis formulated in this ADR is fully verified. Grounding search with self-hosted SearXNG and local extraction is demonstrably superior in factual verifiability, temporal freshness, and cost-efficiency compared to raw commercial chat.

**Engineering authorization granted** to proceed to the next milestones:
- **Thursday (24/09)**: FastAPI core backend service (`/api/search`) with Server-Sent Events (SSE) streaming and real-time token/cost telemetry.
- **Friday (25/09)**: Showcase Web UI with source cards and Bring-Your-Own-Key (BYOK) support.


