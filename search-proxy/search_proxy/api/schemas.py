from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search inquiry")
    lang: str = Field("en", description="Language code (e.g. en, pt, es)")
    max_results: int = Field(10, ge=1, le=20, description="Maximum number of search results to retrieve")
    model: str | None = Field(None, description="Optional LLM model override")
    base_url: str | None = Field(None, description="Optional LLM base URL override")
    api_key: str | None = Field(None, description="Optional LLM API key override")


class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str
    domain: str = ""


class ExtractedDocItem(BaseModel):
    url: str
    status: str
    title: str
    word_count: int


class CitationItem(BaseModel):
    label: str
    url: str


class LatencyBreakdown(BaseModel):
    search_ms: int
    extract_ms: int
    synthesis_ms: int
    total_ms: int


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Telemetry(BaseModel):
    latencies: LatencyBreakdown
    tokens: TokenUsage
    cost_usd: float
    model: str


class SearchResponse(BaseModel):
    query: str
    answer: str
    citations: list[CitationItem]
    sources: list[SearchResultItem]
    extracted_docs: list[ExtractedDocItem]
    telemetry: Telemetry


class HealthResponse(BaseModel):
    status: str
    searxng_connected: bool
    searxng_url: str
    default_model: str
    version: str = "0.1.0"


class ModelPricingItem(BaseModel):
    model: str
    input_per_m: float
    output_per_m: float


class ModelsResponse(BaseModel):
    default_model: str
    recommended_models: list[str]
    pricing: list[ModelPricingItem]
