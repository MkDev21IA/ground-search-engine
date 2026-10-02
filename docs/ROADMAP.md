# Next Week Roadmap: Code Review, Hardening & Public Launch

**Target Week:** October 5 – October 9, 2026  
**Document Version:** 1.0  
**Status:** Approved Plan  
**Repository:** `ground-search-engine`  

---

## 🎯 Executive Objectives

Having concluded all benchmark evaluations and established verifiable superiority on the official ASQA benchmark ([ADR 0016](../decisions/0016-external-validation-vs-literature-baselines.md) and [`results/CONSOLIDATED_BENCHMARK_REPORT.md`](../results/CONSOLIDATED_BENCHMARK_REPORT.md)), the focus of this week is twofold:

1. **Deep Code Review & Quality Audit (Monday – Wednesday)**: Systematically audit, clean, type-check, and harden the Python backend, ethical extraction pipeline, and zero-build web interface.
2. **Public Dissemination & Launch Preparation (Thursday – Friday)**: Package the repository for public release, create visual showcase assets, draft launch publications, and release **v0.1.0**.

---

## 🗓️ Day-by-Day Schedule & Milestones

### 1. Monday (Oct 5, 2026): Core Search Engine & Extractor Audit

* **Target Directories:** `search-proxy/search_proxy/adapters/`, `search-proxy/search_proxy/extractor/`, `search-proxy/search_proxy/models.py`.
* **Key Tasks:**
  - [ ] **Network & Extraction Resilience**: Audit timeout handling, connection pooling, and error propagation in `SearxngAdapter` and `EthicalExtractor`.
  - [ ] **PDF & HTML Edge Cases**: Stress-test edge-case documents (malformed HTML DOMs, encrypted/image-only PDFs, non-UTF8 encodings).
  - [ ] **Strict Typing & Linting**: Run `mypy` and `ruff`/`flake8` to ensure 100% type annotation coverage on all extraction data models.
  - [ ] **Dead Code Cleanup**: Audit imports and remove any obsolete or unused utility functions per `AGENTS.md`.
* **Exit Criteria:** All adapter and extractor unit tests pass offline with zero linting/typing warnings.

---

### 2. Tuesday (Oct 6, 2026): Synthesis Engine & Streaming API Audit

* **Target Directories:** `search-proxy/search_proxy/synthesis/`, `search-proxy/search_proxy/api/` (`app.py`, `routes.py`, `schemas.py`).
* **Key Tasks:**
  - [ ] **SSE Streaming Lifecycle**: Audit Server-Sent Events (`/api/search/stream`) for graceful disconnect handling, client abort signals, and buffer flushing.
  - [ ] **Telemetry & Cost Accuracy**: Validate token calculation formulas and USD pricing logic across model families (OpenAI, Gemini, OpenRouter, and local inference).
  - [ ] **Knowledge Gap Detection**: Verify that prompt instructions reliably force explicit refusal/gap acknowledgments on ungrounded queries.
  - [ ] **Unit & Integration Test Suite**: Expand unit tests in `search-proxy/tests/` to maintain 100% offline determinism and high branch coverage.
* **Exit Criteria:** `python -m pytest -v` runs in under 5 seconds with zero flakes.

---

### 3. Wednesday (Oct 7, 2026): Web UI Polish & Local Sovereignty Walkthrough

* **Target Directories:** `search-proxy/search_proxy/ui/` (`index.html`, `app.js`, `styles.css`) and local setup configurations.
* **Key Tasks:**
  - [ ] **UI/UX Audit**: Test the single-page interface across multiple screen sizes, validating typography, scrollbars, and dark-theme contrast.
  - [ ] **Citation Hover & Navigation**: Verify that hovering over inline citations smoothly highlights and auto-scrolls to the corresponding evidence card.
  - [ ] **Air-Gapped Local Inference Test**: Run an end-to-end live test using **Ollama** (`http://localhost:11434/v1`) running `llama3.2:3b` and `qwen2.5:7b` with internet search enabled, proving 100% private, sovereign on-prem operation.
  - [ ] **BYOK Security Check**: Ensure API keys stored in browser `localStorage` are never exposed in backend server logs or URL query strings.
* **Exit Criteria:** Fully validated web interface operating seamlessly on both commercial cloud endpoints and local Ollama instances.

---

### 4. Thursday (Oct 8, 2026): Visual Asset Pack & Repository Polish

* **Target Directories:** Root `README.md`, `LICENSE`, `CONTRIBUTING.md`, `docs/assets/`.
* **Key Tasks:**
  - [ ] **Interactive Visual Assets**:
    - Capture high-resolution screenshots of the UI in action (Search, Source Cards, Citation Hover, Telemetry Drawer).
    - Record an animated GIF demonstrating real-time streaming and citation provenance.
  - [ ] **Documentation Polish**:
    - Add clear status badges to root `README.md` (License, Python 3.11+, Docker SearXNG, Tests Passing).
    - Write a clean, 3-step **"Quickstart in 60 Seconds"** guide for first-time open-source users.
  - [ ] **Open-Source Readiness**:
    - Review `LICENSE` and include a `CONTRIBUTING.md` outlining the ADR governance process for community contributors.
* **Exit Criteria:** A visually compelling GitHub landing page ready to convert visitors into contributors and stars.

---

### 5. Friday (Oct 9, 2026): Public Dissemination & v0.1.0 Release

* **Target Outputs:** Release tag `v0.1.0`, technical announcement copy, social distribution.
* **Key Tasks:**
  - [ ] **GitHub Release Tag**: Tag and publish **`v0.1.0`** with comprehensive changelog and release notes.
  - [ ] **Technical Launch Publications**:
    - **Hacker News (Show HN)**: Focus on zero-build simplicity, ethical deep extraction vs. naive RAG, and micro-cost economics ($0.58/1k queries).
    - **Reddit (r/LocalLLaMA & r/MachineLearning)**: Emphasize the empirical ASQA benchmark findings (3B/7B open models beating 70B models and GPT-4o via context depth).
    - **LinkedIn / X (Twitter)**: Executive summary highlighting data sovereignty, verified citations, and the end of hallucinated AI search.
* **Exit Criteria:** Public release published and announcements dispatched across target developer communities.

---

## 📋 Readiness Checklist for Release v0.1.0

- [x] All 16 Architecture Decision Records (ADRs) finalized and indexed in [`decisions/README.md`](../decisions/README.md).
- [x] Consolidated benchmark evaluation report published in [`results/CONSOLIDATED_BENCHMARK_REPORT.md`](../results/CONSOLIDATED_BENCHMARK_REPORT.md).
- [x] Multi-tier ASQA benchmark SVG chart embedded in root `README.md`.
- [ ] Complete codebase audit and typing check completed (Monday – Tuesday).
- [ ] Air-gapped Ollama local execution verified (Wednesday).
- [ ] UI screenshots and demo GIF saved in `docs/assets/` (Thursday).
- [ ] Release `v0.1.0` published (Friday).
