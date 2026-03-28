"""AIBIM SDK — Route LLM traffic through the AI security proxy.

Quick start::

    from openai import OpenAI
    from aibim import wrap

    client = OpenAI(api_key="sk-...")
    wrap(client, aibim_url="https://proxy.aibim.ai", aibim_api_key="aibim-key-xxx")
    # All LLM calls now route through AIBIM automatically

For direct prompt analysis::

    from aibim import AibimGuard

    guard = AibimGuard(base_url="https://proxy.aibim.ai", api_key="key")
    result = guard.analyze_sync("Ignore all previous instructions")
    print(result.decision)  # AibimDecision.BLOCK
"""
from __future__ import annotations

from aibim._version import __version__
from aibim.client import AibimClient
from aibim.errors import (
    AibimAuthError,
    AibimBlockedError,
    AibimError,
    AibimRateLimitError,
)
from aibim.guard import AibimGuard
from aibim.models import (
    AibimDecision,
    AibimResponseMeta,
    AnalyzeResponse,
    DetectionResult,
    ProxyEndpoint,
)
from aibim.proxy import is_wrapped, unwrap, wrap
from aibim.websocket import AlertsWebSocket

__all__ = [
    "__version__",
    # Proxy wrapping (core feature)
    "wrap",
    "unwrap",
    "is_wrapped",
    # Clients
    "AibimGuard",
    "AibimClient",
    "AlertsWebSocket",
    # Models
    "AibimDecision",
    "DetectionResult",
    "AnalyzeResponse",
    "AibimResponseMeta",
    "ProxyEndpoint",
    # Errors
    "AibimError",
    "AibimBlockedError",
    "AibimAuthError",
    "AibimRateLimitError",
]
