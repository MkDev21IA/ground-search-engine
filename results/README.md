# Search & Synthesis Evaluation Results

Raw benchmark outputs from each evaluation run of [`search-proxy`](../search-proxy/) against the [`prompts`](../prompts/) suite, stored for subsequent verification and analysis (see [decisions/0006](../decisions/0006-search-evaluation-methodology.md)).

## Convention

One immutable subdirectory per evaluation run, named `YYYY-MM-DD-short-description/` (e.g., `2026-09-17-synthesis-evaluation/`), containing:

- Canonical results files (e.g., `searxng.json`, `synthesis.json`, `report.md`) documenting prompts, retrieved sources, citations, and LLM responses;
- Qualitative notes describing latency, error rates, or WAF challenges encountered.

Raw results are never modified in-place after generation — any new run or correction generates a new timestamped subdirectory to preserve traceable historical data.
