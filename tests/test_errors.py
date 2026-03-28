"""Tests for error types."""
from aibim.errors import AibimError, AibimBlockedError, AibimAuthError, AibimRateLimitError


def test_aibim_error():
    err = AibimError("test", status_code=500)
    assert err.message == "test"
    assert err.status_code == 500
    assert str(err) == "test"


def test_aibim_error_no_status():
    err = AibimError("something went wrong")
    assert err.message == "something went wrong"
    assert err.status_code is None


def test_aibim_error_repr():
    err = AibimError("test", status_code=500)
    assert "AibimError" in repr(err)
    assert "500" in repr(err)


def test_blocked_error():
    err = AibimBlockedError(
        message="blocked",
        risk_score=0.9,
        matched_rules=["R1"],
        correlation_id="abc",
    )
    assert err.risk_score == 0.9
    assert err.matched_rules == ["R1"]
    assert err.correlation_id == "abc"
    assert err.status_code == 403


def test_blocked_error_is_aibim_error():
    err = AibimBlockedError(
        message="blocked",
        risk_score=0.9,
        matched_rules=["R1"],
    )
    assert isinstance(err, AibimError)
    assert err.correlation_id is None


def test_blocked_error_repr():
    err = AibimBlockedError(
        message="blocked",
        risk_score=0.9,
        matched_rules=["R1"],
        correlation_id="abc",
    )
    r = repr(err)
    assert "AibimBlockedError" in r
    assert "0.9" in r


def test_auth_error():
    err = AibimAuthError()
    assert err.status_code == 401
    assert err.message == "Authentication failed"


def test_auth_error_custom_message():
    err = AibimAuthError(message="Invalid token")
    assert err.message == "Invalid token"
    assert err.status_code == 401


def test_rate_limit_error():
    err = AibimRateLimitError(retry_after=5.0)
    assert err.retry_after == 5.0
    assert err.status_code == 429


def test_rate_limit_error_no_retry_after():
    err = AibimRateLimitError()
    assert err.retry_after is None
    assert err.status_code == 429
    assert err.message == "Rate limit exceeded"


def test_rate_limit_error_repr():
    err = AibimRateLimitError(retry_after=5.0)
    assert "AibimRateLimitError" in repr(err)
    assert "5.0" in repr(err)


def test_error_hierarchy():
    """All AIBIM errors should be catchable with a single except clause."""
    errors = [
        AibimError("e"),
        AibimBlockedError(message="b", risk_score=0.5, matched_rules=[]),
        AibimAuthError(),
        AibimRateLimitError(),
    ]
    for err in errors:
        assert isinstance(err, AibimError)
        assert isinstance(err, Exception)
