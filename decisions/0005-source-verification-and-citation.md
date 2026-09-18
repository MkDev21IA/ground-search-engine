# 0005 — Source Verification and Citation

**Status:** Accepted (direction); implementation open
**Date:** 2026-08-27

## Context

[0001](0001-goal-and-scope.md) mandates that virtually every substantive factual claim must cite a source. Merely instructing a model to output URLs is insufficient: LLMs frequently hallucinate fabricated URLs, point to dead links, or cite authentic sources that do not actually support the stated claim. The fundamental product requirement is **grounded, verifiable truth** — sources must be authentic, resolvable, and directly supportive of the assertions made.

## Decision

Source citation is treated as a deterministic engineering pipeline with distinct stages, rather than the sole unguided responsibility of the LLM:

1. **Grounded Generation (RAG)**: The model never cites from internal memory alone — every claim is generated directly from context snippets or full text retrieved during the search phase, and citations point inline to specific resolvable URLs.
2. **Deterministic Source Verification**:
   - **Link existence and resolution**: The target URL resolves with HTTP 200 (preventing hallucinated URLs);
   - **Textual support (claim-level entailment)**: The extracted document text substantively entails the claim made by the model (preventing out-of-context misattribution);
   - **Admitting knowledge gaps**: If retrieved documents do not contain evidence answering the prompt, the model must explicitly state the information gap rather than fabricating ungrounded claims.

## Consequences

- Search, content extraction, and claim verification are core architectural pillars of equal importance to model inference.
- Downstream verification (evaluating claim entailment via RAGAS/NLI) is specified in [0010](0010-citation-verification-ragas-nli.md).
- Search query routing and privacy protections are addressed via local proxying in [0006](0006-search-evaluation-methodology.md).
