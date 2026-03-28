"""Tests for AibimGuard creation and configuration."""
import pytest
from aibim.guard import AibimGuard


def test_guard_defaults():
    guard = AibimGuard()
    assert guard._client._base_url == "http://localhost:8080"
    assert guard._client._api_key is None


def test_guard_custom_config():
    guard = AibimGuard(
        base_url="https://proxy.aibim.ai",
        api_key="test-key",
    )
    assert guard._client._base_url == "https://proxy.aibim.ai"
    assert guard._client._api_key == "test-key"


def test_guard_sync_context_manager():
    with AibimGuard() as guard:
        assert guard._client is not None


@pytest.mark.asyncio
async def test_guard_async_context_manager():
    async with AibimGuard() as guard:
        assert guard._client is not None
