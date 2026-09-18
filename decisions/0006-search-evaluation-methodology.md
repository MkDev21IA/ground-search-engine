# 0006 — Search Engine Evaluation Methodology and Infrastructure

**Status:** Accepted
**Date:** 2026-08-27

## Context

[0005](0005-source-verification-and-citation.md) left the choice of search backends open. Candidates evaluated (self-hosted SearXNG, Brave Search API, Tavily, Exa; the Bing API was discontinued on August 11, 2025) feature different APIs, payload structures, and default behaviors. Testing each engine in an ad-hoc manner would contaminate comparative evaluation — output variances might stem from query formatting rather than intrinsic search quality.

## Decision

1. **Versioned test prompt suite in [`prompts/`](../prompts/)**: Tracked in `prompts_v1.yaml`, covering representative categories (`trivial`, `open-research`, `long-tail`).
2. **Canonical Search Proxy in [`search-proxy/`](../search-proxy/)**: Normalizes every test prompt into a canonical `Query` before dispatching to any search engine, and converts responses into a single canonical `Result` format. Each search engine becomes an adapter.
   - Stack: **Python** — universal HTTP client ecosystem, compatible with local and remote inference pipelines.
   - Core component: Designed to become the permanent search module of the synthesis pipeline, rather than a disposable test harness.
3. **Raw benchmark results in [`results/`](../results/)**: Saved as immutable timestamped directories (`YYYY-MM-DD-description/`).
4. **Evaluation criteria**: Coverage, domain diversity, engine neutrality, content extraction success rate, privacy, latency, and rate limits.

## Implementation (2026-08-27)

`search-proxy` implemented in Python: canonical models (`Query`/`Result`), `SearchAdapter` (ABC), and engine adapter for `searxng` (self-hosted with JSON format enabled). Failures return a structured `Result` with an error field rather than unhandled exceptions. Test suites run 100% offline with mocked HTTP.

## Revision (2026-08-27): Versioning Prompt Files

Prompt files are versioned explicitly (`prompts_v1.yaml`, `prompts_v2.yaml`, etc.) to maintain comparability across historical benchmark runs saved in `results/`. Old versions are preserved as immutable baselines.

## Revision (2026-09-01): Terminology — "queries" to "prompts"

The folder `queries/` was renamed to `prompts/`, and `queries_v1.yaml` became `prompts_v1.yaml`. The input is the natural language question a user submits to an assistant; the proxy transforms this prompt into a search query.

## Revision (2026-09-04): Brave, Tavily, and Exa Excluded — SearXNG as Sole Search Engine

1. **Cost and account requirements**: Brave eliminated its free API tier in February 2026, requiring credit cards and metered billing.
2. **Privacy**: Using commercial APIs ties every user search query and extracted page content to a billing identity, conflicting with [0004](0004-conversation-privacy-and-security.md).
3. **SearXNG adopted as canonical engine**:
   - Self-hosted, routing queries without advertising tracking or user account identification.
   - Operates with `safesearch: 0` (unfiltered), maintaining neutrality per [0002](0002-neutrality-and-factual-moderation.md).

## Revision (2026-09-14): Anti-Scraping Mitigation via Polite Crawl Delay and Engine Redundancy

Initial burst tests against local SearXNG triggered rate limiting from upstream engines.
Adopted architectural mitigations:
1. **Polite crawl delay**: Added `delay_seconds` (default 2.5s) in batch evaluation loops.
2. **Privacy engine redundancy in SearXNG**: Enabled privacy-first engines without tracking or login requirements:
   - **[Mojeek](https://www.mojeek.com/)**: Independent index without search tracking.
   - **[Qwant](https://about.qwant.com/)**: European privacy-focused engine without user profiling.
   - **DuckDuckGo**: Preserved with polite crawl spacing.
