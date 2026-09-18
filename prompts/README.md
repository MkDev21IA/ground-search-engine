# Test Prompts

A versioned collection of research prompts — the natural language questions a user submits to the engine — used to evaluate search engines and the end-to-end grounded synthesis pipeline (see [`../search-proxy/`](../search-proxy/) and [`decisions/0006-search-evaluation-methodology.md`](../decisions/0006-search-evaluation-methodology.md)).

## Versioning

Active file: **`prompts_v1.yaml`**.

Convention: Any revision that alters benchmark comparability with past evaluation runs (category changes, evaluation criteria changes, etc.) must be saved as a new version (`prompts_v2.yaml`, `prompts_v3.yaml`, etc.) rather than modifying an existing version in-place. Older files are preserved to enable historical regression testing against earlier evaluation results stored in `../results/`.

Adding a single prompt within existing categories does not require a new file version — simply assign the next free `id` in the current file.

## Schema

`prompts_v1.yaml` contains a YAML list of prompt objects with the following fields:

- `id`: Stable numeric identifier (never reorder or reuse IDs).
- `category`: `trivial`, `open-research`, `long-tail` (see Categories below).
- `prompt`: Natural language inquiry as submitted by a user.
- `lang`: Language code (`en`, `pt`, etc.).
- `notes`: (Optional) Qualitative guidelines on what constitutes a thorough answer and authoritative primary sources.

## Categories

- **`trivial`**: Factual common-knowledge questions that test pipeline baseline sanity (e.g., speed of light, historical dates). Kept deliberately minimal (2 prompts).
- **`open-research`**: Multidisciplinary synthesis inquiries (health, science, history, economics, technology, public policy) requiring aggregation of multiple authoritative sources — the primary use case of the engine.
- **`long-tail`**: Niche scientific or regional inquiries (biodiversity, environmental monitoring, regional energy statistics) where deep retrieval of primary sources is decisive.

## How to Extend

To add a new prompt, append an entry to the active file (`prompts_v1.yaml`) with the next available `id`. If modifying existing categories in a way that breaks comparability, create a new version file per the "Versioning" section above.
