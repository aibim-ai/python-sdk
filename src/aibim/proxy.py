"""AIBIM proxy wrapping for OpenAI and Anthropic clients.

The ``wrap()`` function is the primary entry point for routing LLM
traffic through the AIBIM security proxy. It works by modifying the
client's base URL and injecting AIBIM-specific headers so that all
subsequent API calls transparently pass through AIBIM's detection
pipeline.

Usage::

    from openai import OpenAI
    from aibim import wrap

    client = OpenAI(api_key="sk-...")
    wrap(client, aibim_url="https://proxy.aibim.ai", aibim_api_key="aibim-key-xxx")
    # All calls now route through AIBIM

    # To restore the original client:
    from aibim import unwrap
    unwrap(client)
"""
from __future__ import annotations

from typing import Any, Optional


_AIBIM_ATTR = "_aibim_original_base_url"
_AIBIM_PROVIDER_ATTR = "_aibim_provider_type"


def _detect_provider(client: Any) -> str:
    """Detect the LLM provider from the client object.

    Returns:
        Provider string: 'openai', 'anthropic', or 'unknown'.
    """
    module = getattr(type(client), "__module__", "") or ""
    qualname = type(client).__qualname__ or ""
    combined = f"{module}.{qualname}".lower()

    if "openai" in combined:
        return "openai"
    if "anthropic" in combined:
        return "anthropic"
    return "unknown"


def _set_base_url(client: Any, url: str) -> str | None:
    """Set the base URL on a client, returning the previous value.

    Handles both OpenAI (``base_url`` property) and Anthropic
    (``base_url`` or ``_base_url``) patterns.
    """
    original: str | None = None

    # OpenAI v1+ exposes base_url as a property that returns an httpx.URL
    if hasattr(client, "base_url"):
        original = str(client.base_url)
        try:
            client.base_url = url
        except (AttributeError, TypeError):
            # Some clients have read-only base_url; try _base_url
            if hasattr(client, "_base_url"):
                original = str(client._base_url)
                client._base_url = url
    elif hasattr(client, "_base_url"):
        original = str(client._base_url)
        client._base_url = url

    return original


def _inject_header(client: Any, key: str, value: str) -> None:
    """Inject a custom header into the client.

    Tries multiple patterns used by different SDK versions:
    - OpenAI v1+: ``_custom_headers`` dict
    - Anthropic: ``_custom_headers`` dict
    - Fallback: ``default_headers`` dict
    """
    if hasattr(client, "_custom_headers") and isinstance(client._custom_headers, dict):
        client._custom_headers[key] = value
    elif hasattr(client, "default_headers") and isinstance(client.default_headers, dict):
        client.default_headers[key] = value
    else:
        # Last resort: create _custom_headers
        if not hasattr(client, "_custom_headers"):
            client._custom_headers = {}
        client._custom_headers[key] = value


def _remove_header(client: Any, key: str) -> None:
    """Remove a custom header from the client."""
    if hasattr(client, "_custom_headers") and isinstance(client._custom_headers, dict):
        client._custom_headers.pop(key, None)
    if hasattr(client, "default_headers") and isinstance(client.default_headers, dict):
        client.default_headers.pop(key, None)


def wrap(
    client: Any,
    aibim_url: str = "http://localhost:8080",
    aibim_api_key: Optional[str] = None,
) -> Any:
    """Wrap an OpenAI or Anthropic client to route traffic through AIBIM.

    Detects the client type automatically and reconfigures it to send
    requests to the AIBIM proxy instead of the original provider URL.
    The original base URL is stored so it can be restored with ``unwrap()``.

    Args:
        client: An OpenAI or Anthropic client instance.
        aibim_url: The AIBIM proxy URL.
        aibim_api_key: Optional AIBIM API key for tenant identification.

    Returns:
        The same client instance (mutated in place), for chaining.
    """
    if hasattr(client, _AIBIM_ATTR):
        return client  # Already wrapped

    provider = _detect_provider(client)

    # Swap base URL
    original = _set_base_url(client, aibim_url)
    if original is None:
        raise ValueError(
            f"Cannot wrap client of type {type(client).__name__}: "
            "no base_url or _base_url attribute found."
        )

    # Store originals for unwrap
    setattr(client, _AIBIM_ATTR, original)
    setattr(client, _AIBIM_PROVIDER_ATTR, provider)

    # Inject AIBIM API key for tenant identification
    if aibim_api_key:
        _inject_header(client, "X-AIBIM-API-Key", aibim_api_key)

    # Mark the provider type so AIBIM proxy knows the upstream format
    if provider != "unknown":
        _inject_header(client, "X-AIBIM-Provider", provider)

    return client


def unwrap(client: Any) -> Any:
    """Restore the original base URL, removing AIBIM routing.

    Args:
        client: A previously wrapped client instance.

    Returns:
        The same client instance with original settings restored.
    """
    if not hasattr(client, _AIBIM_ATTR):
        return client

    original = getattr(client, _AIBIM_ATTR)
    _set_base_url(client, original)

    # Clean up AIBIM headers
    _remove_header(client, "X-AIBIM-API-Key")
    _remove_header(client, "X-AIBIM-Provider")

    # Remove marker attributes
    delattr(client, _AIBIM_ATTR)
    if hasattr(client, _AIBIM_PROVIDER_ATTR):
        delattr(client, _AIBIM_PROVIDER_ATTR)

    return client


def is_wrapped(client: Any) -> bool:
    """Check if a client is currently wrapped through AIBIM.

    Args:
        client: An LLM client instance.

    Returns:
        True if the client is currently routing through AIBIM.
    """
    return hasattr(client, _AIBIM_ATTR)
