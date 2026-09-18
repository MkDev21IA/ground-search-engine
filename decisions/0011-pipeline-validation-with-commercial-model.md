# 0011 — Pipeline Validation with Commercial Model Before Downscaling to Local Inference

**Status:** Accepted
**Date:** 2026-09-04

## Context

Testing the end-to-end mechanics of the pipeline (search → extraction [0009](0009-source-content-extraction.md) → grounded synthesis with inline citations → verification [0010](0010-citation-verification-ragas-nli.md)) exclusively on small local models (7B–8B, [0003](0003-llm-model-architecture.md)) conflates two distinct failure modes: bugs in pipeline orchestration vs. model capability limitations. Using a highly capable reference model isolates the variable: if citation structure fails here, it is an engineering defect in the pipeline, not a weak model.

## Decision

1. **Validate pipeline mechanics first with a capable reference model** (via API key).
2. **Explicit, temporary privacy trade-off**: Using commercial APIs sends prompts and retrieved context off-machine, accepted consciously strictly during integration testing.
3. **Representative prompt evaluation**: Benchmark against standard categories (`trivial`, `open-research`, `long-tail`) to verify citation mechanics.
4. **Focus on groundedness and inline citation precision**: Validate inline markdown links `[Source Title](URL)`, source aggregation, and contradiction handling.

## Consequences

- Validates end-to-end integration before downscaling to local quantizations.
- Any capable OpenAI-compatible endpoint can be used (e.g., `gemini-2.5-flash`).

## Revision (2026-09-17): Implementation of Synthesis Module and Universal OpenAI-Compatible Client

The `search_proxy.synthesis` module was implemented:
1. **Universal Protocol (OpenAI Chat Completions)**: Implemented directly over `httpx` using `/chat/completions`, eliminating heavy SDK dependencies. Compatible with Google Gemini (via its OpenAI compatibility endpoint) and local servers (LM Studio, vLLM, Ollama).
2. **Graceful Degradation in Context (`context.py`)**: Extracted documents (`status == 'ok'`) provide `full_text`. Extraction failures gracefully fall back to search snippets (`source_tier: snippet`).
3. **Factual Prompting and Inline Citations (`prompts.py`)**: System prompts mandate inline markdown citations `[Title](URL)` using provided URLs, requiring the model to note discrepancies and admit gaps.
4. **Decoding Parameters**: Default `temperature: 0.2` balances grounded fidelity with fluent generation.
5. **Default Model Selection (`gemini-2.5-flash`)**: Chosen for high processing speed, low cost per million tokens, and strong adherence to structured citation instructions.
