# 0004 — Conversation Privacy and Security

**Status:** Accepted (direction); implementation open
**Date:** 2026-08-27

## Context

A research chatbot routinely handles inquiries on sensitive matters (health, personal inquiries, policy controversies) — especially given the goal in [0002](0002-neutrality-and-factual-moderation.md) of answering without reflexive refusals. This makes conversation privacy a core architectural requirement, not an afterthought.

Reference architecture: Duck.ai (DuckDuckGo AI Chat). Its model, per public documentation ([Duck.ai privacy](https://duckduckgo.com/duckduckgo-help-pages/duckai/ai-chat-privacy)):
- Acts as a **proxy** between the user and model providers: the model provider never sees the end-user directly.
- **Strips identifying metadata** (e.g., user IP addresses) before dispatching prompts.
- **Does not log or store conversations by default**, and queries are not used for model training.
- Enforces data processing agreements with model providers limiting data retention.
- Optional synchronization features store history with **end-to-end encryption** where DuckDuckGo itself cannot read conversations.

## Decision

Adopt the same privacy-first principles for this project, aligned with the self-hosted/open architecture of [0003](0003-llm-model-architecture.md):

1. **Data minimization**: Do not persist conversations by default; session persistence (if implemented) must be strictly opt-in.
2. **No unnecessary identity linkage**: Never bind search queries or conversation logs to personal identifiers (IP, email, device fingerprints) beyond what is strictly necessary for ephemeral session execution.
3. **Encryption in transit and at rest**: Mandatory TLS in transit; local encryption at rest for any optionally saved session data.
4. **Local sovereignty**: When local inference is utilized ([0003](0003-llm-model-architecture.md)), privacy is solved by design: prompts and context never leave the local environment.

### Relationship with Search and Retrieval

When inference runs locally, prompt leakage to third-party model providers is eliminated. The primary privacy exposure shifts to the **search and retrieval stage** ([0005](0005-source-verification-and-citation.md)), which by nature queries search backends with user keywords. This motivates the use of self-hosted meta-search engines (SearXNG) that strip identifying headers and aggregate queries anonymously without ad tracking.

## Consequences

- This sets an architectural **direction**: implementation details for encryption at rest and session management remain open for future ADRs.
- Search queries routed through external search engines must be scrubbed of tracking cookies and identifying user headers.
- Reinforces [0002](0002-neutrality-and-factual-moderation.md) and [0003](0003-llm-model-architecture.md) in prioritizing local, sovereign execution.
