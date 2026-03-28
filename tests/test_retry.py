"""Tests for RetryPolicy."""
import pytest
import httpx

from aibim.retry import RetryPolicy


def test_retry_policy_defaults():
    policy = RetryPolicy()
    assert policy.max_retries == 3
    assert policy.backoff_factor == 0.5
    assert policy.max_backoff_secs == 30.0


def test_retry_policy_custom():
    policy = RetryPolicy(max_retries=5, backoff_factor=1.0, max_backoff_secs=60.0)
    assert policy.max_retries == 5
    assert policy.backoff_factor == 1.0
    assert policy.max_backoff_secs == 60.0


def test_compute_delay_exponential():
    policy = RetryPolicy(backoff_factor=1.0, max_backoff_secs=120.0)
    # Delay should increase with attempts (base delay = factor * 2^attempt)
    d0 = policy._compute_delay(0)
    d1 = policy._compute_delay(1)
    d2 = policy._compute_delay(2)
    # Base: 1*1=1, 1*2=2, 1*4=4 (plus jitter up to 50%)
    assert 1.0 <= d0 <= 1.5
    assert 2.0 <= d1 <= 3.0
    assert 4.0 <= d2 <= 6.0


def test_compute_delay_respects_max():
    policy = RetryPolicy(backoff_factor=10.0, max_backoff_secs=5.0)
    delay = policy._compute_delay(5)
    assert delay <= 5.0


def test_compute_delay_uses_retry_after_header():
    policy = RetryPolicy()
    response = httpx.Response(429, headers={"retry-after": "2.5"})
    delay = policy._compute_delay(0, response)
    assert delay == 2.5


def test_compute_delay_retry_after_capped():
    policy = RetryPolicy(max_backoff_secs=1.0)
    response = httpx.Response(429, headers={"retry-after": "10"})
    delay = policy._compute_delay(0, response)
    assert delay == 1.0


def test_is_retryable_http_status():
    for status in (429, 500, 502, 503, 504):
        request = httpx.Request("GET", "http://test")
        response = httpx.Response(status, request=request)
        exc = httpx.HTTPStatusError("err", request=request, response=response)
        retryable, resp = RetryPolicy._is_retryable(exc)
        assert retryable, f"Status {status} should be retryable"
        assert resp is response


def test_is_not_retryable_400():
    request = httpx.Request("GET", "http://test")
    response = httpx.Response(400, request=request)
    exc = httpx.HTTPStatusError("err", request=request, response=response)
    retryable, _ = RetryPolicy._is_retryable(exc)
    assert not retryable


def test_is_retryable_connect_error():
    request = httpx.Request("GET", "http://test")
    exc = httpx.ConnectError("conn failed", request=request)
    retryable, resp = RetryPolicy._is_retryable(exc)
    assert retryable
    assert resp is None


def test_is_not_retryable_generic():
    retryable, _ = RetryPolicy._is_retryable(ValueError("nope"))
    assert not retryable


def test_execute_sync_success():
    policy = RetryPolicy(max_retries=2)
    result = policy.execute_sync(lambda: 42)
    assert result == 42


def test_execute_sync_retries_then_succeeds():
    call_count = 0

    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            request = httpx.Request("GET", "http://test")
            response = httpx.Response(500, request=request)
            raise httpx.HTTPStatusError("err", request=request, response=response)
        return "ok"

    policy = RetryPolicy(max_retries=3, backoff_factor=0.01)
    result = policy.execute_sync(flaky)
    assert result == "ok"
    assert call_count == 3


def test_execute_sync_exhausted():
    def always_fail():
        request = httpx.Request("GET", "http://test")
        response = httpx.Response(500, request=request)
        raise httpx.HTTPStatusError("err", request=request, response=response)

    policy = RetryPolicy(max_retries=1, backoff_factor=0.01)
    with pytest.raises(httpx.HTTPStatusError):
        policy.execute_sync(always_fail)


def test_execute_sync_non_retryable_raises_immediately():
    call_count = 0

    def fail_400():
        nonlocal call_count
        call_count += 1
        request = httpx.Request("GET", "http://test")
        response = httpx.Response(400, request=request)
        raise httpx.HTTPStatusError("err", request=request, response=response)

    policy = RetryPolicy(max_retries=3, backoff_factor=0.01)
    with pytest.raises(httpx.HTTPStatusError):
        policy.execute_sync(fail_400)
    assert call_count == 1  # No retries for 400


@pytest.mark.asyncio
async def test_execute_async_success():
    policy = RetryPolicy(max_retries=2)

    async def fn():
        return 42

    result = await policy.execute(fn)
    assert result == 42


@pytest.mark.asyncio
async def test_execute_async_retries_then_succeeds():
    call_count = 0

    async def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            request = httpx.Request("GET", "http://test")
            response = httpx.Response(502, request=request)
            raise httpx.HTTPStatusError("err", request=request, response=response)
        return "ok"

    policy = RetryPolicy(max_retries=3, backoff_factor=0.01)
    result = await policy.execute(flaky)
    assert result == "ok"
    assert call_count == 3
