from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from search_proxy.api.app import app
from search_proxy.extractor.models import ExtractedDocument
from search_proxy.models import Result
from search_proxy.synthesis.models import SynthesisOutput, Citation


def make_result(
    title: str = "Test",
    url: str = "https://example.com",
    snippet: str = "Test snippet",
    rank: int = 1,
    engine: str = "searxng",
    fetched_at: str = "2026-09-23T12:00:00Z",
) -> Result:
    return Result(
        engine=engine,
        url=url,
        title=title,
        snippet=snippet,
        rank=rank,
        fetched_at=fetched_at,
    )


def make_doc(
    url: str = "https://example.com",
    title: str | None = "Test",
    text: str | None = "Text",
    content_type: str = "text/html",
    status: str = "ok",
    extractor_used: str | None = "trafilatura",
    fetched_at: str = "2026-09-23T12:00:00Z",
) -> ExtractedDocument:
    return ExtractedDocument(
        url=url,
        title=title,
        text=text,
        content_type=content_type,
        status=status,
        extractor_used=extractor_used,
        fetched_at=fetched_at,
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_ok(client: TestClient) -> None:
    with patch("search_proxy.api.routes.SearxngAdapter.search") as mock_search:
        mock_search.return_value = [make_result()]
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["searxng_connected"] is True
        assert "default_model" in data


def test_health_searxng_degraded(client: TestClient) -> None:
    with patch("search_proxy.api.routes.SearxngAdapter.search") as mock_search:
        mock_search.side_effect = RuntimeError("Connection refused")
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "degraded"
        assert data["searxng_connected"] is False


def test_models_catalog(client: TestClient) -> None:
    res = client.get("/api/models")
    assert res.status_code == 200
    data = res.json()
    assert "default_model" in data
    assert len(data["recommended_models"]) > 0
    assert len(data["pricing"]) > 0
    model_names = [p["model"] for p in data["pricing"]]
    assert "llama-3.2-3b" in model_names


def test_search_sync_endpoint(client: TestClient) -> None:
    mock_results = [
        make_result(
            title="Speed of Light",
            url="https://physics.org/c",
            snippet="299,792,458 m/s",
        )
    ]
    mock_docs = [
        make_doc(
            url="https://physics.org/c",
            title="Speed of Light",
            text="The speed of light in vacuum is exactly 299,792,458 m/s.",
            status="ok",
        )
    ]
    mock_synthesis = SynthesisOutput(
        prompt="speed of light",
        answer="The speed of light is 299,792,458 m/s [Source](https://physics.org/c).",
        citations=[Citation(label="Source", url="https://physics.org/c")],
        sources_used=["https://physics.org/c"],
        model="meta-llama/llama-3.2-3b-instruct",
        generated_at="2026-09-23T12:00:00Z",
        raw_usage={"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120, "cost": 0.000015},
    )

    with patch("search_proxy.api.routes.SearxngAdapter.search", return_value=mock_results), \
         patch("search_proxy.api.routes.ContentExtractor.extract_many", return_value=mock_docs), \
         patch("search_proxy.api.routes.SynthesisService.synthesize", return_value=mock_synthesis):

        payload = {"query": "speed of light", "lang": "en"}
        res = client.post("/api/search", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["query"] == "speed of light"
        assert "299,792,458 m/s" in data["answer"]
        assert len(data["citations"]) == 1
        assert data["citations"][0]["url"] == "https://physics.org/c"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["domain"] == "physics.org"
        assert data["telemetry"]["tokens"]["total_tokens"] == 120
        assert data["telemetry"]["cost_usd"] == 0.000015


def test_search_sync_validation_error(client: TestClient) -> None:
    res = client.post("/api/search", json={"query": ""})
    assert res.status_code == 422


def test_search_stream_sse(client: TestClient) -> None:
    mock_results = [
        make_result(
            title="Test",
            url="https://example.org/test",
            snippet="Snippet text",
        )
    ]
    mock_docs = [
        make_doc(
            url="https://example.org/test",
            title="Test Page",
            text="Contextual text content.",
            status="ok",
        )
    ]
    stream_chunks = [
        {"type": "token", "content": "Grounded "},
        {"type": "token", "content": "answer [Link](https://example.org/test)."},
        {"type": "usage", "usage": {"prompt_tokens": 50, "completion_tokens": 10, "total_tokens": 60}},
    ]

    with patch("search_proxy.api.routes.SearxngAdapter.search", return_value=mock_results), \
         patch("search_proxy.api.routes.ContentExtractor.extract_many", return_value=mock_docs), \
         patch("search_proxy.api.routes.LLMClient.stream_generate", return_value=stream_chunks):

        res = client.get("/api/search/stream?q=quantum+physics")
        assert res.status_code == 200
        assert "text/event-stream" in res.headers["content-type"]

        body = res.text
        assert "event: status" in body
        assert "event: search_results" in body
        assert "event: extraction_complete" in body
        assert "event: token" in body
        assert "event: citations" in body
        assert "event: telemetry" in body
        assert "event: done" in body
        assert "https://example.org/test" in body


def test_byok_headers_override(client: TestClient) -> None:
    mock_results = [make_result()]
    mock_docs = [make_doc()]
    mock_synthesis = SynthesisOutput(
        prompt="test",
        answer="Answer",
        citations=[],
        sources_used=[],
        model="custom/my-model",
        generated_at="2026-09-23T12:00:00Z",
        raw_usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    )

    def mock_synth(query, results, extracted_docs):
        return mock_synthesis

    with patch("search_proxy.api.routes.SearxngAdapter.search", return_value=mock_results), \
         patch("search_proxy.api.routes.ContentExtractor.extract_many", return_value=mock_docs), \
         patch("search_proxy.api.routes.SynthesisService.synthesize", side_effect=mock_synth), \
         patch("search_proxy.api.routes.LLMClient.__init__", return_value=None) as mock_client_init:

        headers = {
            "X-LLM-API-Key": "custom-sk-12345",
            "X-LLM-Base-URL": "http://localhost:11434/v1",
            "X-LLM-Model": "ollama/custom-model",
        }
        res = client.post("/api/search", json={"query": "test"}, headers=headers)
        assert res.status_code == 200

        # Verify LLMClient was initialized with the custom config
        call_kwargs = mock_client_init.call_args.kwargs
        cfg = call_kwargs["config"]
        assert cfg.api_key == "custom-sk-12345"
        assert cfg.base_url == "http://localhost:11434/v1"
        assert cfg.model == "ollama/custom-model"


def test_ui_root_serves_html(client: TestClient) -> None:
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Ground Search" in res.text


def test_ui_static_asset_serves_js(client: TestClient) -> None:
    res = client.get("/static/app.js")
    assert res.status_code == 200
    assert "Ground Search Engine" in res.text


