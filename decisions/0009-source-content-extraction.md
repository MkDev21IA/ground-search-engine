# 0009 — Source Content Extraction (Fetch and Parsing)

**Status:** Accepted (extraction mechanics); citation verification addressed in [0010](0010-citation-verification-ragas-nli.md)
**Date:** 2026-09-02

## Context

The [`search-proxy`](../search-proxy/) returns URL + title + snippet — not the full document text. This is insufficient for the core requirement of [0005](0005-source-verification-and-citation.md): verifying that cited claims exist in the underlying source. A robust mechanism is required to fetch and extract clean textual content from arbitrary URLs.

## Decision

### Main Content Extraction: Mature Libraries over Ad-hoc Heuristics

Custom HTML parsing heuristics (e.g., extracting the largest `<div>`) fail across heterogeneous sites. Use established content extraction libraries:
- **`trafilatura`** as the primary extractor (top benchmark F1 score for boilerplate removal in English text).
- **`readability-lxml`** as automatic fallback when `trafilatura` returns empty text.

### Content-Type Routing

Route content extraction based on the HTTP response `Content-Type` header:
- `text/html` → `trafilatura` / `readability-lxml`
- `application/pdf` → `pypdf`

### JavaScript-Rendered SPAs: Measure Before Adding Heavy Browsers

Headless browsers (Playwright/Puppeteer) are resource-intensive. Most reference domains (news, scientific papers, government portals) serve server-rendered HTML. Fetch with standard HTTP first; if extracted text falls below a minimal character threshold, classify the document as `needs_js`.

### Ethical Fetching: robots.txt and Polite User-Agent

Respect `robots.txt` via standard library `urllib.robotparser`, respect crawl delays, and identify the crawler with an honest User-Agent: `LLMSearchBot/0.1 (+https://github.com/MkDev21IA/grounded-search-engine)`.

### Graceful Degradation and Top-K Redundancy

Avoid brittle domain-specific scraping patches or insecure SSL bypasses. The architecture relies on two universal principles:
1. **Top-K redundancy**: Fetching top candidate links; extracting 70–80% as full text provides ample context for synthesis.
2. **Snippet fallback**: If full text extraction fails (e.g., HTTP 403, network timeout, dead link), gracefully degrade by inheriting the search snippet with marked provenance (`source_tier: snippet`).

## Revision (2026-09-15): Module Structure and Deterministic Fixtures

Implemented as `search_proxy.extractor` within `search-proxy/`. Offline test fixtures in `tests/fixtures/` (`sample_article.html`, `sample_report.pdf`, `robots.txt`) guarantee deterministic unit testing without live network dependencies.

## Revision (2026-09-16): Adoption of `pypdf` for PDF Extraction

Adopted **`pypdf`** under the BSD-3-Clause license: pure Python, lightweight, fast metadata and text stream extraction, avoiding heavy binary C++ compilation dependencies.
