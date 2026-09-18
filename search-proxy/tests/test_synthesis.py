from __future__ import annotations

import json
import httpx
import pytest

from search_proxy.extractor.models import ExtractedDocument
from search_proxy.models import Result
from search_proxy.synthesis import (
    LLMClient,
    LLMConfig,
    SynthesisService,
    build_context,
    build_synthesis_messages,
    extract_citations,
    truncate_text,
)


def test_truncate_text():
    short_text = "One two three four five"
    assert truncate_text(short_text, max_words=10) == short_text

    long_text = "word " * 20
    truncated = truncate_text(long_text, max_words=5)
    assert len(truncated.split()) > 5
    assert "truncated" in truncated
    assert truncated.startswith("word word word word word... [content truncated")


def test_build_context_uses_full_text_and_snippet_fallback():
    results = [
        Result(
            engine="searxng",
            rank=1,
            title="Full Article",
            url="https://example.com/article",
            snippet="Article snippet",
            fetched_at="2026-09-17T10:00:00Z",
        ),
        Result(
            engine="searxng",
            rank=2,
            title="Page with Error 403",
            url="https://example.com/blocked",
            snippet="Search snippet preserved for blocked page",
            fetched_at="2026-09-17T10:00:00Z",
        ),
    ]

    extracted_docs = [
        ExtractedDocument(
            url="https://example.com/article",
            title="Extracted Title",
            text="Full detailed textual content of extracted article.",
            content_type="text/html",
            status="ok",
            extractor_used="trafilatura",
            fetched_at="2026-09-17T10:00:00Z",
        ),
        ExtractedDocument(
            url="https://example.com/blocked",
            title=None,
            text=None,
            content_type="text/html",
            status="http_error",
            extractor_used=None,
            fetched_at="2026-09-17T10:00:00Z",
            error="HTTP 403 Forbidden",
        ),
    ]

    context_str, sources = build_context(results, extracted_docs)

    assert len(sources) == 2

    # Source 1: Full Text
    assert sources[0].index == 1
    assert sources[0].source_tier == "full_text"
    assert sources[0].title == "Extracted Title"
    assert "Full detailed textual content" in sources[0].content

    # Source 2: Snippet Fallback
    assert sources[1].index == 2
    assert sources[1].source_tier == "snippet"
    assert sources[1].title == "Page with Error 403"
    assert "Search snippet preserved" in sources[1].content

    # Verification of assembled string
    assert "--- [SOURCE 1] ---" in context_str
    assert "Evidence Tier: Extracted Full Text" in context_str
    assert "--- [SOURCE 2] ---" in context_str
    assert "Evidence Tier: Search Snippet" in context_str


def test_build_context_respects_max_total_words():
    results = [
        Result(
            engine="searxng",
            rank=1,
            title="Doc 1",
            url="https://example.com/1",
            snippet="word " * 50,
            fetched_at="2026-09-17T10:00:00Z",
        ),
        Result(
            engine="searxng",
            rank=2,
            title="Doc 2",
            url="https://example.com/2",
            snippet="word " * 50,
            fetched_at="2026-09-17T10:00:00Z",
        ),
    ]
    # max_total_words=60 allows Doc 1 (50 words) but prevents Doc 2 (+50 > 60)
    context_str, sources = build_context(results, [], max_total_words=60)

    assert len(sources) == 1
    assert sources[0].url == "https://example.com/1"
    assert "https://example.com/2" not in context_str


def test_extract_citations():
    text = (
        "According to the [Scientific Observatory](https://science.org/article), the project started in 2024. "
        "Another study [Energy Report](https://energy.gov/report.pdf) confirms the numbers. "
        "Repeating the source [Scientific Observatory](https://science.org/article) should not duplicate."
    )
    citations = extract_citations(text)

    assert len(citations) == 2
    assert citations[0].label == "Scientific Observatory"
    assert citations[0].url == "https://science.org/article"
    assert citations[1].label == "Energy Report"
    assert citations[1].url == "https://energy.gov/report.pdf"


def test_build_synthesis_messages():
    messages = build_synthesis_messages(query="What is the budget?", context="Source 1: $5 billion")

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "You are an advanced, objective research assistant" in messages[0]["content"]
    assert "Mandatory Inline Markdown Citations" in messages[0]["content"]

    assert messages[1]["role"] == "user"
    assert "What is the budget?" in messages[1]["content"]
    assert "Source 1: $5 billion" in messages[1]["content"]


def test_llm_client_mock_success():
    captured_requests = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        body = json.loads(request.read())
        assert body["model"] == "gemini-2.5-flash"
        assert body["temperature"] == 0.2
        assert len(body["messages"]) == 2

        response_data = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "The budget is 5 billion according to the [Report](https://energy.gov).",
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 30,
                "total_tokens": 180,
            },
        }
        return httpx.Response(200, json=response_data)

    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as http_client:
        config = LLMConfig(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key="test-key-123",
            model="gemini-2.5-flash",
            temperature=0.2,
        )
        client = LLMClient(config=config, http_client=http_client)

        messages = [
            {"role": "system", "content": "Be factual."},
            {"role": "user", "content": "What is the budget?"},
        ]
        answer, usage = client.generate(messages)

        assert "5 billion" in answer
        assert usage["total_tokens"] == 180
        assert len(captured_requests) == 1
        req = captured_requests[0]
        assert req.headers["Authorization"] == "Bearer test-key-123"
        assert str(req.url) == "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


def test_llm_client_mock_error_handling():
    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "Invalid API key"}})

    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as http_client:
        config = LLMConfig(api_key="invalid-key")
        client = LLMClient(config=config, http_client=http_client)

        with pytest.raises(RuntimeError) as exc_info:
            client.generate([{"role": "user", "content": "Hello"}])

        assert "LLM API request failed [401]" in str(exc_info.value)
        assert "Invalid API key" in str(exc_info.value)


def test_synthesis_service_orchestration():
    def mock_handler(request: httpx.Request) -> httpx.Response:
        response_data = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "The James Webb telescope was developed by [NASA](https://nasa.gov/jwst) and ESA.",
                    }
                }
            ],
            "usage": {"total_tokens": 120},
        }
        return httpx.Response(200, json=response_data)

    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as http_client:
        client = LLMClient(http_client=http_client)
        service = SynthesisService(llm_client=client)

        results = [
            Result(
                engine="searxng",
                rank=1,
                title="NASA JWST",
                url="https://nasa.gov/jwst",
                snippet="James Webb space telescope mission",
                fetched_at="2026-09-17T10:00:00Z",
            )
        ]
        extracted_docs = [
            ExtractedDocument(
                url="https://nasa.gov/jwst",
                title="NASA JWST",
                text="The James Webb Space Telescope is a space observatory developed by NASA.",
                content_type="text/html",
                status="ok",
                extractor_used="trafilatura",
                fetched_at="2026-09-17T10:00:00Z",
            )
        ]

        output = service.synthesize(
            query="Who developed the James Webb Telescope?",
            results=results,
            extracted_docs=extracted_docs,
        )

        assert output.prompt == "Who developed the James Webb Telescope?"
        assert "James Webb telescope was developed" in output.answer
        assert len(output.citations) == 1
        assert output.citations[0].label == "NASA"
        assert output.citations[0].url == "https://nasa.gov/jwst"
        assert len(output.sources_used) == 1
        assert output.sources_used[0].source_tier == "full_text"
        assert output.raw_usage["total_tokens"] == 120
        assert output.model == "gemini-2.5-flash"
        assert output.generated_at is not None
