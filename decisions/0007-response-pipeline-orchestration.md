# 0007 — Response Pipeline Orchestration: LangGraph and Multi-Language Search

**Status:** Accepted (lightweight native asyncio pipeline adopted; heavy graph frameworks deferred)  
**Date:** 2026-09-01  

## Context

Following search normalization ([0006](0006-search-evaluation-methodology.md)), the synthesis agent must execute the complete cycle: search → content extraction → grounded synthesis with inline citations → verification. The adoption of **LangGraph** (agent graph orchestration framework from LangChain) was proposed for multi-hop tool-loops.

## Analysis of LangGraph

### Advantages
- Graph orchestration with state persistence, conditional looping, and checkpointing for long-running workflows.

### Disadvantages and Risks
- Latency and cost overhead: agentic multi-turn loops add considerable latency and token cost compared to deterministic linear pipelines.
- Unnecessary complexity for single-turn grounded Q&A.
- Built-in tool wrappers do not match the strict canonical contract and privacy audits enforced by our custom `search-proxy` ([0004](0004-conversation-privacy-and-security.md), [0006](0006-search-evaluation-methodology.md)). If LangGraph is ever evaluated later, `search-proxy` must be wrapped as a custom tool, never replaced.

## Decision

**Do not adopt LangGraph at this stage.** Build the linear pipeline first with native asynchronous Python (`asyncio`). Evaluate stateful agent frameworks only if dynamic cyclic reasoning (e.g., iterative query reformulations upon failed retrieval) proves indispensable in practice.

## Multi-Language Search Fan-Out

The pipeline supports parallel multi-language retrieval:
1. **Semantic Query Expansion**: When beneficial (e.g., technical or international topics), infer 1–2 target languages (e.g., German for European standards, Mandarin for semiconductor supply chains, English for global scientific research).
2. **Parallel Dispatch**: Run searches across target languages concurrently using `asyncio.gather`.
3. **Interleaved Aggregation**: Balance retrieved links across languages prior to content extraction ([0009](0009-source-content-extraction.md)).
4. **Final Synthesis**: The answer is synthesized in the user's conversational language, preserving citations to foreign primary sources.

## Consequences

- Keep orchestration lightweight, relying on simple `asyncio` and `httpx`.
- Avoid premature framework abstractions before measuring pipeline bottlenecks.

## Revision (2026-10-02): Linear Async Pipeline Validated Across Production & Benchmarks

The decision to avoid heavy graph frameworks (LangGraph) was conclusively validated:
1. **Execution Simplicity & Zero-Build**: Native `asyncio` with `httpx` allowed seamless integration with FastAPI streaming SSE endpoints ([0014](0014-backend-service-architecture-and-telemetry.md)) and the lightweight web interface ([0015](0015-showcase-web-interface-and-citation-ux.md)).
2. **Deterministic Latency**: By avoiding unconstrained agent loops, pipeline latency remained predictable (15s–25s total including network search, HTML extraction, and token synthesis).
3. **Reproducible Benchmarking**: The linear async architecture executed 948 benchmark questions deterministically with complete telemetry and cost tracking ([0016](0016-external-validation-vs-literature-baselines.md)).

