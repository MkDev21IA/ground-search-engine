from __future__ import annotations

import json
from pathlib import Path

from search_proxy import runner
from search_proxy.base import SearchAdapter
from search_proxy.models import Query, Result


class _FakeAdapter(SearchAdapter):
    name = "fake"

    def search(self, query: Query) -> list[Result]:
        if query.text == "breaks":
            return [
                Result(
                    engine=self.name,
                    url="",
                    title="",
                    snippet="",
                    rank=0,
                    fetched_at="2026-08-27T00:00:00Z",
                    error="simulated failure",
                )
            ]
        return [
            Result(
                engine=self.name,
                url="https://example.com",
                title="Example",
                snippet="snippet text",
                rank=1,
                fetched_at="2026-08-27T00:00:00Z",
            )
        ]


def test_run_writes_canonical_json_and_survives_per_prompt_errors(tmp_path, monkeypatch):
    monkeypatch.setitem(runner.ADAPTERS, "fake", _FakeAdapter)

    prompts_path = tmp_path / "prompts.yaml"
    prompts_path.write_text(
        """
- id: 1
  category: trivial
  prompt: "normal question"
  lang: en
- id: 2
  category: trivial
  prompt: "breaks"
  lang: en
""".strip(),
        encoding="utf-8",
    )

    out_dir = tmp_path / "out"
    out_file = runner.run("fake", prompts_path, out_dir)

    assert out_file == out_dir / "fake.json"
    data = json.loads(out_file.read_text(encoding="utf-8"))

    assert len(data) == 2
    assert data[0]["prompt_id"] == 1
    assert data[0]["results"][0]["url"] == "https://example.com"
    assert data[1]["results"][0]["error"] == "simulated failure"


def test_run_rejects_unknown_engine(tmp_path):
    prompts_path = tmp_path / "prompts.yaml"
    prompts_path.write_text("- id: 1\n  category: trivial\n  prompt: \"x\"\n", encoding="utf-8")

    try:
        runner.run("nonexistent-engine", prompts_path, tmp_path / "out")
        raise AssertionError("should have raised ValueError")
    except ValueError:
        pass
