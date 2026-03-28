"""AIBIM SDK WebSocket client for real-time alert streaming.

Connects to the AIBIM WebSocket endpoint and yields alert events
as they occur in real time.

Usage::

    from aibim import AlertsWebSocket

    async with AlertsWebSocket(base_url="https://proxy.aibim.ai", api_key="key") as ws:
        async for alert in ws.listen():
            print(f"Alert: {alert}")
"""
from __future__ import annotations

import json
from typing import Any, AsyncIterator, Optional

import websockets
from websockets.asyncio.client import ClientConnection


class AlertsWebSocket:
    """Real-time alert streaming via WebSocket.

    Connects to ``/ws/alerts`` and yields parsed JSON alert events.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
    ) -> None:
        ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self._url = f"{ws_url}/ws/alerts"
        self._api_key = api_key
        self._ws: Optional[ClientConnection] = None

    async def connect(self) -> None:
        """Establish WebSocket connection."""
        headers: dict[str, str] = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        self._ws = await websockets.connect(self._url, additional_headers=headers)

    async def listen(self) -> AsyncIterator[dict[str, Any]]:
        """Async iterator yielding alert events as parsed JSON dicts.

        Yields:
            Parsed alert event dictionaries.

        Raises:
            RuntimeError: If not connected. Call ``connect()`` first
                          or use the async context manager.
        """
        if self._ws is None:
            raise RuntimeError("WebSocket not connected. Call connect() or use async with.")
        async for message in self._ws:
            if isinstance(message, bytes):
                message = message.decode("utf-8")
            yield json.loads(message)

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def __aenter__(self) -> AlertsWebSocket:
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
