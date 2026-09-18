from __future__ import annotations

from pathlib import Path
import httpx
import pytest

from search_proxy.extractor import (
    ContentExtractor,
    RobotsChecker,
    extract_html_content,
    extract_pdf_content,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_extract_article_cleans_boilerplate_and_keeps_content():
    html = (FIXTURES_DIR / "sample_article.html").read_text(encoding="utf-8")
    title, text, extractor_used, status = extract_html_content(html)

    assert status == "ok"
    assert extractor_used == "trafilatura"
    assert title is not None and "Fusão Nuclear" in title
    assert text is not None

    # Main content must be present
    assert "fusão nuclear comercial atingiu marcos históricos" in text
    assert "Commonwealth Fusion Systems" in text

    # Boilerplate / ads / cookie notices must be excluded
    assert "Compre agora seu curso de Python" not in text
    assert "Este site usa cookies" not in text
    assert "Todos os direitos reservados" not in text


def test_detect_needs_js_on_spa():
    html = (FIXTURES_DIR / "sample_spa.html").read_text(encoding="utf-8")
    title, text, extractor_used, status = extract_html_content(html)

    assert status == "needs_js"
    assert text is None or len(text) < 100


def test_robots_checker_respects_rules():
    robots_txt = (FIXTURES_DIR / "sample_robots_disallowed.txt").read_text(encoding="utf-8")

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=robots_txt)
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as client:
        checker = RobotsChecker()
        assert not checker.is_allowed("https://example.com/restricted/page.html", client=client)
        assert not checker.is_allowed("https://example.com/private/data.html", client=client)
        assert checker.is_allowed("https://example.com/public/artigo.html", client=client)


def test_service_orchestrates_extraction_and_robots():
    robots_txt = (FIXTURES_DIR / "sample_robots_disallowed.txt").read_text(encoding="utf-8")
    article_html = (FIXTURES_DIR / "sample_article.html").read_text(encoding="utf-8")

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=robots_txt)
        if request.url.path == "/public/article.html":
            return httpx.Response(
                200,
                headers={"content-type": "text/html; charset=utf-8"},
                text=article_html,
            )
        if request.url.path == "/private/secret.html":
            return httpx.Response(
                200,
                headers={"content-type": "text/html; charset=utf-8"},
                text=article_html,
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as client:
        service = ContentExtractor(client=client)

        # Case 1: Blocked by robots.txt
        doc_blocked = service.extract_from_url("https://example.com/private/secret.html")
        assert doc_blocked.status == "blocked_robots"
        assert doc_blocked.text is None

        # Case 2: Allowed and extracted successfully
        doc_ok = service.extract_from_url("https://example.com/public/article.html")
        assert doc_ok.status == "ok"
        assert doc_ok.text is not None
        assert "fusão nuclear" in doc_ok.text
        assert doc_ok.extractor_used == "trafilatura"


def test_fallback_to_readability_when_trafilatura_returns_none(monkeypatch):
    html = (FIXTURES_DIR / "sample_article.html").read_text(encoding="utf-8")

    import trafilatura

    # Simulate trafilatura failure
    monkeypatch.setattr(trafilatura, "extract", lambda *args, **kwargs: None)

    title, text, extractor_used, status = extract_html_content(html)
    assert status == "ok"
    assert extractor_used == "readability"
    assert text is not None and "fusão nuclear" in text


def test_extract_pdf_cleans_and_reads_metadata():
    pdf_bytes = (FIXTURES_DIR / "sample_report.pdf").read_bytes()
    title, text, extractor_used, status = extract_pdf_content(pdf_bytes)

    assert status == "ok"
    assert extractor_used == "pypdf"
    assert title == "Relatorio Tecnico de Transicao Energetica 2026"
    assert text is not None
    assert "tecnologias solares e sistemas de armazenamento" in text


def test_service_orchestrates_pdf_extraction():
    pdf_bytes = (FIXTURES_DIR / "sample_report.pdf").read_bytes()

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.path == "/docs/report.pdf":
            return httpx.Response(
                200,
                headers={"content-type": "application/pdf"},
                content=pdf_bytes,
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    with httpx.Client(transport=transport) as client:
        service = ContentExtractor(client=client)
        doc = service.extract_from_url("https://example.com/docs/report.pdf")

        assert doc.status == "ok"
        assert doc.content_type == "application/pdf"
        assert doc.extractor_used == "pypdf"
        assert doc.title == "Relatorio Tecnico de Transicao Energetica 2026"
        assert doc.text is not None and "tecnologias solares" in doc.text
