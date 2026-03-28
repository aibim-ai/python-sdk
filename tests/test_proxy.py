"""Tests for wrap/unwrap proxy functionality."""
import pytest
from aibim import wrap, unwrap, is_wrapped


class MockOpenAIClient:
    def __init__(self):
        self.base_url = "https://api.openai.com/v1"


class MockAnthropicClient:
    def __init__(self):
        self.base_url = "https://api.anthropic.com"
        self._custom_headers = {}


def test_wrap_changes_base_url():
    client = MockOpenAIClient()
    wrap(client, aibim_url="https://proxy.aibim.ai")
    assert "proxy.aibim.ai" in str(client.base_url)


def test_unwrap_restores_url():
    client = MockOpenAIClient()
    original = str(client.base_url)
    wrap(client, aibim_url="https://proxy.aibim.ai")
    unwrap(client)
    assert str(client.base_url) == original


def test_is_wrapped():
    client = MockOpenAIClient()
    assert not is_wrapped(client)
    wrap(client, aibim_url="https://proxy.aibim.ai")
    assert is_wrapped(client)
    unwrap(client)
    assert not is_wrapped(client)


def test_wrap_idempotent():
    client = MockOpenAIClient()
    wrap(client, aibim_url="https://proxy.aibim.ai")
    url_after_first = str(client.base_url)
    wrap(client, aibim_url="https://other.proxy.ai")  # second wrap should be no-op
    assert is_wrapped(client)
    assert str(client.base_url) == url_after_first


def test_unwrap_not_wrapped():
    client = MockOpenAIClient()
    result = unwrap(client)  # should not raise
    assert result is client


def test_wrap_injects_api_key():
    client = MockOpenAIClient()
    wrap(client, aibim_url="https://proxy.aibim.ai", aibim_api_key="test-key")
    assert is_wrapped(client)
    assert client._custom_headers["X-AIBIM-API-Key"] == "test-key"


def test_wrap_returns_client():
    client = MockOpenAIClient()
    result = wrap(client, aibim_url="https://proxy.aibim.ai")
    assert result is client


def test_wrap_anthropic_client():
    client = MockAnthropicClient()
    wrap(client, aibim_url="https://proxy.aibim.ai", aibim_api_key="test-key")
    assert is_wrapped(client)
    assert client._custom_headers["X-AIBIM-API-Key"] == "test-key"
    assert str(client.base_url) == "https://proxy.aibim.ai"


def test_unwrap_removes_headers():
    client = MockAnthropicClient()
    wrap(client, aibim_url="https://proxy.aibim.ai", aibim_api_key="test-key")
    unwrap(client)
    assert "X-AIBIM-API-Key" not in client._custom_headers


def test_wrap_without_api_key():
    client = MockOpenAIClient()
    wrap(client, aibim_url="https://proxy.aibim.ai")
    assert is_wrapped(client)
    # No X-AIBIM-API-Key header should be injected
    headers = getattr(client, "_custom_headers", {})
    assert "X-AIBIM-API-Key" not in headers
