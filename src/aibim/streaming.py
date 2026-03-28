"""AIBIM streaming response wrapper.

Wraps httpx streaming responses to provide async iteration over
SSE chunks while exposing AIBIM detection metadata from response headers.
"""
from __future__ import annotations

from typing import AsyncIterator

import httpx

from aibim.models import AibimResponseMeta


class AibimStreamResponse:
    """Wraps an httpx streaming response for SSE consumption.

    Parses ``x-aibim-*`` headers from the response to expose detection
    metadata, and yields SSE data chunks as an async iterator.

    Usage::

        async with client.stream("POST", "/v1/chat/completions", json=payload) as resp:
            stream = AibimStreamResponse(resp)
            print(f"Decision: {stream.detection_meta.decision}")
            async for chunk in stream:
                process(chunk)
    """

    def __init__(self, response: httpx.Response) -> None:
        self._response = response
        self._meta = AibimResponseMeta.from_headers(dict(response.headers))

    @property
    def detection_meta(self) -> AibimResponseMeta:
        """AIBIM detection metadata parsed from response headers."""
        return self._meta

    @property
    def status_code(self) -> int:
        """HTTP status code of the response."""
        return self._response.status_code

    @property
    def headers(self) -> httpx.Headers:
        """Raw response headers."""
        return self._response.headers

    async def __aiter__(self) -> AsyncIterator[str]:
        """Async iterate over SSE data chunks.

        Yields the data payload of each ``data: ...`` SSE line.
        Stops when ``data: [DONE]`` is encountered.
        """
        async for line in self._response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    break
                yield data
            # Skip empty lines and other SSE fields (event:, id:, retry:)

    async def read_all(self) -> list[str]:
        """Read all SSE data chunks into a list.

        Returns:
            List of data payloads from SSE lines.
        """
        chunks: list[str] = []
        async for chunk in self:
            chunks.append(chunk)
        return chunks

    async def close(self) -> None:
        """Close the underlying response stream."""
        await self._response.aclose()

    async def __aenter__(self) -> AibimStreamResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
