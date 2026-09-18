# Architecture Decision Records (ADRs)

This directory records product and architectural decisions for the project using the ADR (Architecture Decision Record) format: one markdown file per decision, numbered sequentially, which is not retroactively rewritten — if a decision changes, a new ADR supersedes or revises it.

Use `template.md` as the baseline for new decisions.

## Possible Statuses

- **Proposed** — Under discussion, not yet finalized. Used to document rationale and alternatives.
- **Accepted** — Approved and currently in effect.
- **Superseded** — Historical decision replaced by a subsequent ADR.

## Index

| # | Decision | Status |
|---|----------|--------|
| [0001](0001-goal-and-scope.md) | Project Goal and Scope | Accepted |
| [0002](0002-neutrality-and-factual-moderation.md) | Neutrality and Factual Objectivity | Accepted |
| [0003](0003-llm-model-architecture.md) | Language Model Architecture (LLM) | Accepted (direction: open-weight and universal OpenAI-compatible) |
| [0004](0004-conversation-privacy-and-security.md) | Conversation Privacy and Security | Accepted (direction); implementation open |
| [0005](0005-source-verification-and-citation.md) | Source Verification and Citation | Accepted (direction); implementation open |
| [0006](0006-search-evaluation-methodology.md) | Search Engine Evaluation Methodology and Infrastructure | Accepted (anti-scraping mitigation revised 2026-09-14) |
| [0007](0007-response-pipeline-orchestration.md) | Response Pipeline Orchestration: LangGraph and Multi-Language Search | Proposed (multi-language search C2 revised 2026-09-14) |
| [0008](0008-future-evaluation-with-promptfoo.md) | Future Evaluation with Promptfoo | Proposed |
| [0009](0009-source-content-extraction.md) | Source Content Extraction (Fetch and Parsing) | Accepted (HTML/PDF extractor revised 2026-09-16) |
| [0010](0010-citation-verification-ragas-nli.md) | Citation Verification: RAGAS First, NLI On-Demand | Accepted (prototype direction) |
| [0011](0011-pipeline-validation-with-commercial-model.md) | Pipeline Validation with Commercial Model Before Downscaling | Accepted (synthesis bridge and OpenAI-compatible client revised 2026-09-17) |
