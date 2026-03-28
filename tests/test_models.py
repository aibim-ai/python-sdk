"""Tests for data models."""
from aibim.models import AibimDecision, AibimResponseMeta, DetectionResult, AnalyzeResponse


def test_aibim_decision_values():
    assert AibimDecision.ALLOW == "allow"
    assert AibimDecision.WARN == "warn"
    assert AibimDecision.BLOCK == "block"


def test_response_meta_from_headers():
    headers = {
        "x-aibim-decision": "block",
        "x-aibim-score": "0.92",
        "x-aibim-cache": "true",
        "x-aibim-cache-tier": "semantic",
        "x-correlation-id": "test-123",
    }
    meta = AibimResponseMeta.from_headers(headers)
    assert meta.decision == AibimDecision.BLOCK
    assert meta.score == 0.92
    assert meta.cache is True
    assert meta.cache_tier == "semantic"
    assert meta.correlation_id == "test-123"


def test_response_meta_defaults():
    meta = AibimResponseMeta.from_headers({})
    assert meta.decision is None
    assert meta.score is None
    assert meta.cache is None
    assert meta.cache_tier is None
    assert meta.correlation_id is None


def test_response_meta_cache_false():
    headers = {"x-aibim-cache": "false"}
    meta = AibimResponseMeta.from_headers(headers)
    assert meta.cache is False


def test_response_meta_invalid_score():
    headers = {"x-aibim-score": "not-a-number"}
    meta = AibimResponseMeta.from_headers(headers)
    assert meta.score is None


def test_response_meta_invalid_decision():
    headers = {"x-aibim-decision": "invalid-value"}
    meta = AibimResponseMeta.from_headers(headers)
    assert meta.decision is None


def test_detection_result():
    result = DetectionResult(
        risk_score=0.85,
        is_threat=True,
        rules_matched=["INJECT_001"],
        model="gpt-4",
        latency_ms=12.5,
    )
    assert result.is_threat
    assert result.risk_score == 0.85
    assert result.rules_matched == ["INJECT_001"]
    assert result.model == "gpt-4"
    assert result.latency_ms == 12.5


def test_detection_result_defaults():
    result = DetectionResult(risk_score=0.0, is_threat=False)
    assert result.rules_matched == []
    assert result.model == "default"
    assert result.latency_ms == 0.0


def test_analyze_response():
    resp = AnalyzeResponse(
        risk_score=0.1,
        is_suspicious=False,
        decision=AibimDecision.ALLOW,
        matched_rules=[],
    )
    assert not resp.is_suspicious
    assert resp.decision == AibimDecision.ALLOW
    assert resp.correlation_id is None


def test_analyze_response_with_rules():
    resp = AnalyzeResponse(
        risk_score=0.95,
        is_suspicious=True,
        decision=AibimDecision.BLOCK,
        matched_rules=["INJECT_001", "JAILBREAK_003"],
        correlation_id="corr-456",
    )
    assert resp.is_suspicious
    assert len(resp.matched_rules) == 2
    assert resp.correlation_id == "corr-456"
