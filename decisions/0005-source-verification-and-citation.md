# 0005 — Source Verification and Citation

**Status:** Accepted  
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

## Revision (2026-10-02): Realization via Trafilatura, Regex Citation Extraction, and ASQA Benchmarking

The citation verification pipeline was fully implemented and benchmarked across [0009](0009-source-content-extraction.md), [0011](0011-pipeline-validation-with-commercial-model.md), [0014](0014-backend-service-architecture-and-telemetry.md), [0015](0015-showcase-web-interface-and-citation-ux.md), and [0016](0016-external-validation-vs-literature-baselines.md):
1. **Pre-Synthesis Verification**: `trafilatura` and `pypdf` fetch documents with strict HTTP 200 checks, extracting clean text while pruning navigation boilerplate and ads.
2. **Synthesis Grounding**: Universal system prompts enforce inline markdown links `[Source Title](URL)` with zero ungrounded extrapolation and mandatory refusal when context is missing.
3. **Post-Synthesis Deterministic Parsing**: Regex-based citation extractor (`extract_citations`) matches model links against the ingested source registry, measuring exact link counts and detecting hallucinated URLs.
4. **Empirical Literature Validation**: In the 948-question ASQA benchmark ([0016](0016-external-validation-vs-literature-baselines.md)), GSE achieved up to 84.0% citation rates with 0% URL hallucinations, significantly outperforming academic baselines.

