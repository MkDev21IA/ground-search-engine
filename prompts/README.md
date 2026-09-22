# Test Prompts

A versioned collection of research prompts — the natural language questions a user submits to the engine — used to evaluate search engines and the end-to-end grounded synthesis pipeline (see [`../search-proxy/`](../search-proxy/) and [`decisions/0006-search-evaluation-methodology.md`](../decisions/0006-search-evaluation-methodology.md)).

## Versioning

## Versioning

- **`prompts_v1.yaml`**: Baseline evaluation suite covering basic factual sanity (`trivial`), broad synthesis (`open-research`), and regional/ecological niches (`long-tail`).
- **`prompts_v2.yaml`**: Advanced stress-test evaluation suite covering high-controversy medical safety, financial/equities CapEx vs ROI, oil and commodity geopolitics, post-quantum cryptography, adversarial premise traps, and cross-border regulatory compliance.

Convention: Any revision that alters benchmark comparability with past evaluation runs (category changes, evaluation criteria changes, etc.) must be saved as a new version (`prompts_v2.yaml`, `prompts_v3.yaml`, etc.) rather than modifying an existing version in-place. Older files are preserved to enable historical regression testing against earlier evaluation results stored in `../results/`.

Adding a single prompt within existing categories does not require a new file version — simply assign the next free `id` in the current file.

## Schema

`prompts_vN.yaml` contains a YAML list of prompt objects with the following fields:

- `id`: Stable numeric identifier (never reorder or reuse IDs).
- `category`: Category tag (e.g. `trivial`, `open-research`, `long-tail`, `medical-controversy`, `financial-equities`, `oil-energy`, `geopolitics`, `cryptography`, `adversarial`).
- `prompt`: Natural language inquiry as submitted by a user.
- `lang`: Language code (`en`, `pt`, etc.).
- `notes`: (Optional) Qualitative guidelines on what constitutes a thorough answer and authoritative primary sources.

## Categories

- **`trivial`**: Factual common-knowledge questions that test pipeline baseline sanity (e.g., speed of light, historical dates). Kept deliberately minimal (2 prompts).
- **`open-research`**: Multidisciplinary synthesis inquiries (health, science, history, economics, technology, public policy) requiring aggregation of multiple authoritative sources — the primary use case of the engine.
- **`long-tail`**: Niche scientific or regional inquiries (biodiversity, environmental monitoring, regional energy statistics) where deep retrieval of primary sources is decisive.
- **`medical-controversy`**: Medical inquiries with conflicting clinical trials or active regulatory pharmacovigilance disputes (e.g., GLP-1 long-term safety, psychedelic therapeutics).
- **`financial-equities`**: Complex equity, CapEx, and earnings valuation debates requiring financial reporting synthesis.
- **`oil-energy`**: Global energy market dynamics, OPEC+ vs non-OPEC quotas, and territorial energy disputes.
- **`geopolitics`**: High-stakes technological competition, trade restrictions, and sanctions.
- **`cryptography`**: Rigorous technical standards with exact parameter sizes and benchmark proofs.
- **`adversarial`**: Traps with false premises designed to test whether the pipeline debunks myths or hallucinates validation.

## How to Extend

To add a new prompt, append an entry to the appropriate file (`prompts_v1.yaml` or `prompts_v2.yaml`) with the next available `id`. If modifying existing categories in a way that breaks comparability, create a new version file per the "Versioning" section above.
