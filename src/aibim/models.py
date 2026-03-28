"""AIBIM SDK data models.

Pydantic models for API responses and detection metadata.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AibimDecision(str, Enum):
    """Decision returned by the AIBIM detection pipeline."""

    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


class DetectionResult(BaseModel):
    """Result from a single detection layer."""

    risk_score: float = Field(ge=0.0, le=1.0, description="Risk score between 0 and 1")
    is_threat: bool = Field(description="Whether the input is classified as a threat")
    rules_matched: list[str] = Field(default_factory=list, description="IDs of matched detection rules")
    model: str = Field(default="default", description="Model identifier used for analysis")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Detection latency in milliseconds")


class AnalyzeResponse(BaseModel):
    """Response from the /api/v1/analyze endpoint."""

    risk_score: float = Field(ge=0.0, le=1.0, description="Aggregate risk score")
    is_suspicious: bool = Field(description="Whether the input is flagged as suspicious")
    decision: AibimDecision = Field(description="Pipeline decision")
    matched_rules: list[str] = Field(default_factory=list, description="IDs of matched rules")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracing")


class AibimResponseMeta(BaseModel):
    """Detection metadata parsed from x-aibim-* response headers.

    When traffic flows through the AIBIM proxy, these headers are added
    to the upstream LLM response so callers can inspect detection results.
    """

    decision: Optional[AibimDecision] = Field(default=None, description="Detection decision")
    score: Optional[float] = Field(default=None, description="Risk score")
    cache: Optional[bool] = Field(default=None, description="Whether response was served from cache")
    cache_tier: Optional[str] = Field(default=None, description="Cache tier (semantic, exact, etc.)")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracing")

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> AibimResponseMeta:
        """Parse x-aibim-* headers into an AibimResponseMeta instance."""
        decision_raw = headers.get("x-aibim-decision")
        score_raw = headers.get("x-aibim-score")
        cache_raw = headers.get("x-aibim-cache")
        cache_tier = headers.get("x-aibim-cache-tier")
        correlation_id = headers.get("x-correlation-id")

        decision = None
        if decision_raw:
            try:
                decision = AibimDecision(decision_raw.lower())
            except ValueError:
                decision = None

        score = None
        if score_raw:
            try:
                score = float(score_raw)
            except (ValueError, TypeError):
                score = None

        cache = None
        if cache_raw is not None:
            cache = cache_raw.lower() in ("true", "1", "yes")

        return cls(
            decision=decision,
            score=score,
            cache=cache,
            cache_tier=cache_tier,
            correlation_id=correlation_id,
        )


class ProxyEndpoint(BaseModel):
    """A configured proxy endpoint."""

    slug: str = Field(description="URL slug for the endpoint")
    name: str = Field(description="Human-readable name")
    upstream_url: str = Field(description="Upstream LLM provider URL")
    upstream_type: str = Field(description="Provider type (openai, anthropic, etc.)")
    is_active: bool = Field(default=True, description="Whether the endpoint is active")
