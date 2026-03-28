"""Tests for AibimClient creation and configuration."""
import pytest
from aibim.client import AibimClient


def test_client_defaults():
    client = AibimClient()
    assert client._base_url == "http://localhost:8080"
    assert client._api_key is None
    assert client._timeout == 30.0


def test_client_custom_config():
    client = AibimClient(
        base_url="https://proxy.aibim.ai",
        api_key="test-key",
        timeout=60.0,
        max_retries=5,
    )
    assert client._base_url == "https://proxy.aibim.ai"
    assert client._api_key == "test-key"
    assert client._timeout == 60.0
    assert client._retry.max_retries == 5


def test_client_strips_trailing_slash():
    client = AibimClient(base_url="https://proxy.aibim.ai/")
    assert client._base_url == "https://proxy.aibim.ai"


def test_client_headers_with_api_key():
    client = AibimClient(api_key="my-key")
    headers = client._headers()
    assert headers["Authorization"] == "Bearer my-key"
    assert headers["Content-Type"] == "application/json"


def test_client_headers_without_api_key():
    client = AibimClient()
    headers = client._headers()
    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/json"


def test_sub_clients_lazy():
    client = AibimClient()
    assert client._auth is None
    assert client._rules is None
    assert client._data is None
    assert client._tenant is None
    assert client._alerts is None


def test_sub_client_access():
    client = AibimClient()
    # Accessing sub-clients should instantiate them lazily
    auth = client.auth
    assert auth is not None
    assert client._auth is auth
    # Second access returns the same instance
    assert client.auth is auth


def test_sub_client_rules():
    client = AibimClient()
    rules = client.rules
    assert rules is not None
    assert client.rules is rules


def test_sub_client_data():
    client = AibimClient()
    data = client.data
    assert data is not None
    assert client.data is data


def test_sub_client_tenant():
    client = AibimClient()
    tenant = client.tenant
    assert tenant is not None
    assert client.tenant is tenant


def test_sub_client_alerts():
    client = AibimClient()
    alerts = client.alerts
    assert alerts is not None
    assert client.alerts is alerts


def test_sync_context_manager():
    with AibimClient() as client:
        assert client._base_url == "http://localhost:8080"
    # After exiting, sync client should be closed if it was opened


@pytest.mark.asyncio
async def test_async_context_manager():
    async with AibimClient() as client:
        assert client._base_url == "http://localhost:8080"


def test_close_sync_no_client():
    """Closing without ever making a request should not raise."""
    client = AibimClient()
    client.close_sync()  # Should not raise


@pytest.mark.asyncio
async def test_close_async_no_client():
    """Closing without ever making a request should not raise."""
    client = AibimClient()
    await client.close()  # Should not raise
