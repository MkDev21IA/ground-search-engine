# 0013 — Architectural Differentiation vs. Google AI Overviews and Search Grounding

**Status:** Accepted  
**Date:** 2026-09-22  

## Context

The rollout of generative search interfaces by major search engines—most notably Google's "AI Overviews" (consumer web search) and official enterprise APIs such as Google Cloud's [Vertex AI Search Grounding](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/ground-with-google-search)—creates an immediate question for stakeholders and end users:

*Why build and self-host an open-source grounded search engine when Google provides an AI mode for free in the browser with source links? Can they be benchmarked head-to-head?*

To maintain technical clarity and product focus, this decision formally documents the architectural, economic, privacy, and neutrality distinctions between `ground-search-engine` and Google's AI offerings, as well as the feasibility of direct automated benchmarking.

## Decision

### 1. Architectural and Product Differentiation Matrix

| Dimension | Google AI Overviews (Consumer Search) | Google Vertex AI Grounding (Enterprise API) | Ground Search Engine (This Project) |
| :--- | :--- | :--- | :--- |
| **Business & Pricing Model** | "Free" to consumer; funded by behavioral data harvesting and targeted ads. | Pay-per-query: **$14.00 per 1,000 search queries** + Gemini token fees ([Google Cloud Pricing](https://cloud.google.com/vertex-ai/pricing)). | **$0.92 to $1.71 per 1,000 searches** (lightweight cloud API) or **$0.00** (100% local Ollama/vLLM). |
| **Programmatic API Access** | **None.** No public API. Requires fragile third-party scrapers that violate Google ToS. | Official REST/gRPC API in Google Cloud ecosystem. | **Open, canonical HTTP API** (`search-proxy`) compatible with any system. |
| **Privacy & Sovereignty** | Zero privacy. Queries, browser fingerprints, and user accounts logged to ad profile. | Enterprise privacy agreement; queries processed in Google Cloud multitenant infra. | **Local sovereignty** ([0004](0004-conversation-privacy-and-security.md)). Self-hosted SearXNG + local extraction + optional local LLM. |
| **Editorial Neutrality & Moderation** | Aggressive commercial suppression of controversial, political, or medical topics. | Subject to Google Cloud generative safety filter policies. | **Neutral and pluralistic** ([0002](0002-neutrality-and-factual-moderation.md)). Unfiltered retrieval (`safesearch: 0`) citing all sides. |
| **Trigger Rate & Determinism** | Intermittent; triggers on only ~15–20% of searches at Google's algorithmic discretion. | Guaranteed per API request. | **100% deterministic**; executes search, extraction, and synthesis on every submitted query. |
| **Auditability & Provenance** | Black-box ranking, invisible scraping, hidden system prompts. | Proprietary Google search index and ranking weights. | **100% open source**. Exact extracted HTML/PDF text, token usage, and citation code are verifiable. |

### 2. Feasibility of Automated Head-to-Head Benchmarking

1. **Consumer Google AI Overviews**:
   - Automated side-by-side evaluation against consumer Google AI Overviews is **operationally infeasible and statistically invalid**. Google does not provide an official API for AI Overviews. Using SERP scrapers (e.g. SerpApi, Bright Data) is brittle, subject to frequent anti-bot blocks, requires CAPTCHA bypassing, and fails to trigger an AI Overview on many queries, corrupting comparative benchmarks.
2. **Enterprise Vertex AI Search Grounding**:
   - Automated benchmarking is technically feasible via Google's official Vertex AI API. However, at **$14.00 per 1,000 search queries** (excluding token costs), running high-volume benchmark sweeps against Vertex AI Grounding would impose commercial API lock-in and high metered costs, contradicting the project's low-cost and local-first evaluation philosophy ([0006](0006-search-evaluation-methodology.md)).

## Consequences

- **Clear Technical Narrative**: Stakeholders and users understand that `ground-search-engine` is not competing with Google as an ad-supported browser interface, but provides an **independent, private, verifiable, and drastically cheaper (93%–100% cost reduction)** factual synthesis infrastructure.
- **Benchmark Focus**: Automated benchmarks will continue to focus on reproducible, universal OpenAI-compatible endpoints and local models where exact costs, token counts, and retrieval parameters can be rigorously audited.
- **Future Work**: If required for commercial sales collateral, a small qualitative manual audit (10 queries) comparing consumer Google AI Overviews against `ground-search-engine` can be documented qualitatively without maintaining a fragile automated scraper harness.
