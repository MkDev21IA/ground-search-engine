# 0003 — Language Model Architecture (LLM)

**Status:** Accepted (direction: open-weight and universal OpenAI-compatible)
**Date:** 2026-08-27 (revised 2026-09-18)

## Context

A grounded synthesis and citation engine requires flexibility in its choice of language model (LLM):

- **Local inference (*local-first*)**: Guarantees total privacy, fine-grained decoding control, and independence from external connectivity or commercial API rate limits.
- **High-throughput compatible APIs**: Provide rapid response latency, negligible per-query cost, and immediate accessibility on resource-constrained hardware (without requiring dedicated high-end GPUs).

Additionally, binding the codebase to proprietary vendor SDKs (e.g., `google-genai` or `openai-python`) creates tight coupling and introduces bloated dependencies.

## Decision

Adopt an architecture centered on a **universal client implementing the standard OpenAI Chat Completions specification (`/chat/completions`) using `httpx`**, free from proprietary SDK dependencies:

1. **Decoupled universal protocol**:
   - All inference traffic is dispatched using standard JSON payloads (`model`, `messages`, `temperature`, etc.).
   - Enables seamless runtime switching between cloud providers (e.g., `gemini-2.5-flash` via Google's OpenAI-compatible endpoint, standard OpenAI) and local self-hosted inference servers (LM Studio, Ollama, vLLM, `llama.cpp server`) purely by adjusting environment variables (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`).

2. **Supported open-weight models**:
   - For local execution, the engine supports standard open-weight families, including:
     - **Qwen 2.5 / Qwen 3** (Alibaba — Apache 2.0)
     - **Llama 3.1 / 3.2 / 3.3** (Meta)
     - **Mistral / Mixtral** (Mistral AI — Apache 2.0)
     - **DeepSeek** (DeepSeek — MIT)
   - On commodity or consumer hardware (e.g., 4GB VRAM or CPU-only execution), Q4_K_M quantizations in the 7B–8B parameter range are prioritized.

3. **Pipeline validation with efficient models**:
   - During active development and synthesis testing, high-throughput models like `gemini-2.5-flash` serve to accelerate iteration and isolate prompt-engineering verification from local hardware constraints (as documented in [0011](0011-pipeline-validation-with-commercial-model.md)).

## Consequences

- The pipeline code (`search-proxy`) remains minimal, portable, and vendor-agnostic.
- The user maintains complete sovereignty over where inference takes place, toggling seamlessly between cloud and 100% offline private execution.
