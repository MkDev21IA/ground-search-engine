# 0002 — Neutrality and Factual Objectivity

**Status:** Accepted
**Date:** 2026-08-27

## Context

Commercial language models frequently refuse or bias answers to legitimate research inquiries (scientific topics, historical controversies, demographic trends, public health debates) due to institutional overcaution or opaque pre-filtering. This compromises the goal of [0001](0001-goal-and-scope.md) — building a knowledge base rigorously anchored in empirical evidence and verifiable sources. Concurrently, any knowledge engine must observe universal legal and ethical safety baselines (e.g., refusing operational instructions for direct physical harm, exploitation, or clearly illegal acts).

## Decision

Adopt a posture focused on **neutrality and balanced evidence synthesis**:

1. **Priority for factual context**: When presented with legitimate research questions, the system responds by presenting data, scientific consensus, and documented divergences directly from retrieved sources, rather than emitting reflexive refusals or patronizing moralizing lectures.
2. **Universal, bounded safeguards**: Only inquiries that constitute actionable instructions for direct harm or unambiguous legal violations warrant refusal; academic, historical, statistical, and theoretical inquiries are answered factually with cited sources.
3. **Balance and impartiality**: Where legitimate scholarly, scientific, or policy debates exist, the pipeline synthesizes and contrasts multiple perspectives, attributing each to its primary origin.

## Consequences

- The synthesis pipeline must remain decoupled from arbitrary third-party moderation filters, reinforcing the model architecture flexibility established in [0003](0003-llm-model-architecture.md).
- System prompts must strictly enforce objectivity, clarity, and grounded evidence, rejecting preachy or editorializing tones.
