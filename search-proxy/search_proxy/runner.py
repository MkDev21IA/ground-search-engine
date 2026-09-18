from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from .adapters.searxng import SearxngAdapter
from .base import SearchAdapter
from .models import Query

ADAPTERS: dict[str, type[SearchAdapter]] = {
    "searxng": SearxngAdapter,
}


def load_prompts(path: Path) -> list[dict[str, Any]]:
    """Load evaluation prompts from a YAML file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or []


def run(
    engine_name: str,
    prompts_path: Path,
    out_dir: Path,
    delay_seconds: float = 0.0,
) -> Path:
    """Run all prompts in `prompts_path` against `engine_name` and save canonical results.

    A failing adapter for an individual prompt will not crash the batch — the error
    is captured inside the Result object (see base.error_result).
    """
    if engine_name not in ADAPTERS:
        raise ValueError(
            f"Unknown engine: {engine_name!r}. Options: {sorted(ADAPTERS)}"
        )

    adapter = ADAPTERS[engine_name]()
    prompts = load_prompts(prompts_path)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{engine_name}.json"

    runs = []
    total = len(prompts)
    for i, entry in enumerate(prompts, start=1):
        if i > 1 and delay_seconds > 0:
            time.sleep(delay_seconds)

        query = Query(
            text=entry["prompt"],
            lang=entry.get("lang", "en"),
            max_results=entry.get("max_results", 10),
        )
        results = adapter.search(query)
        cat = entry.get("category", "uncategorized")
        print(f"[{i}/{total}] Prompt {entry['id']} ({cat}): {len(results)} results")
        runs.append(
            {
                "prompt_id": entry["id"],
                "category": entry.get("category"),
                "prompt": entry["prompt"],
                "results": [asdict(r) for r in results],
            }
        )

    out_file.write_text(
        json.dumps(runs, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out_file
