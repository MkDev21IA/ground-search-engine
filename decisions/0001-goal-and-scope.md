# 0001 — Project Goal and Scope

**Status:** Accepted
**Date:** 2026-08-27

## Context

Commercial LLM chatbots frequently answer research queries without citing the origin of their assertions, or refuse to answer legitimate inquiries due to excessive moderation caution. This undermines the use of LLMs as research and knowledge tools, where traceability of information (the ability to independently verify sources) is just as critical as the answer itself.

## Decision

Build an open research and synthesis engine (LLM) whose primary objective is **grounded knowledge**: users submit research inquiries across diverse domains and receive answers in which **virtually every substantive factual claim is anchored by a verifiable source** (article, web page, research paper, document, etc.), cited inline directly alongside the statement.

Exception: universally accepted common knowledge facts (e.g., "the Earth is spherical") do not require citation — the benchmark rule is "would this claim require a citation in serious academic or journalistic writing?".

### Research Domains

The scope covers open multidisciplinary research without artificial domain restrictions — including science, technology, history, public policy, health, and economics. The objective of the engine is to ensure strict factual grounding and provenance tracking for any legitimate research inquiry.

## Consequences

- Every system response must carry claim-level provenance metadata, rather than merely a generic list of links at the end of the text — this is an architectural requirement, not just a prompting directive (see [0005](0005-source-verification-and-citation.md)).
- The project does not aim to be a general-purpose conversational chatbot (e.g., creative brainstorming, code assistant) — the core use case is factual research and investigation.
- This goal demands strict neutrality and factual objectivity, which motivates [0002](0002-neutrality-and-factual-moderation.md) and [0003](0003-llm-model-architecture.md).
