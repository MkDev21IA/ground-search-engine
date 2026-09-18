from __future__ import annotations

import httpx

from search_proxy.adapters.searxng import SearxngAdapter
from search_proxy.models import Query


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


def test_parses_results_into_canonical_format(monkeypatch):
    payload = {
        "results": [
            {"url": "https://a.example", "title": "A", "content": "snippet a"},
            {"url": "https://b.example", "title": "B", "content": "snippet b"},
        ]
    }

    def fake_get(url, params=None, timeout=None):
        assert params["q"] == "test query"
        assert params["language"] == "en"
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx, "get", fake_get)

    adapter = SearxngAdapter(base_url="http://localhost:8080")
    results = adapter.search(Query(text="test query", lang="en", max_results=10))

    assert [r.url for r in results] == ["https://a.example", "https://b.example"]
    assert [r.rank for r in results] == [1, 2]
    assert all(r.engine == "searxng" and r.error is None for r in results)


def test_respects_max_results(monkeypatch):
    payload = {
        "results": [{"url": f"https://{i}.example", "title": str(i), "content": ""} for i in range(5)]
    }
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _FakeResponse(payload))

    adapter = SearxngAdapter(base_url="http://localhost:8080")
    results = adapter.search(Query(text="test query", max_results=2))

    assert len(results) == 2


def test_http_error_becomes_error_result_instead_of_raising(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise httpx.ConnectError("connection refused", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", fake_get)

    adapter = SearxngAdapter(base_url="http://localhost:8080")
    results = adapter.search(Query(text="test query"))

    assert len(results) == 1
    assert results[0].error is not None
    assert results[0].engine == "searxng"
