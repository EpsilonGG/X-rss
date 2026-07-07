from __future__ import annotations

from datetime import datetime

import httpx

from infrastructure.http.response import RawResponse


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/138.0 Safari/537.36"
)


class HTTPClient:
    def __init__(
        self,
        timeout: int = 20,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": user_agent,
            },
        )

    def get(self, url: str) -> RawResponse:
        response = self._client.get(url)

        response.raise_for_status()

        return RawResponse(
            url=str(response.url),
            status_code=response.status_code,
            content_type=response.headers.get("Content-Type", ""),
            text=response.text,
            fetched_at=datetime.utcnow(),
        )

    def close(self) -> None:
        self._client.close()
