from __future__ import annotations

from fetchers.base import BaseFetcher
from infrastructure.http import HTTPClient
from infrastructure.http import RawResponse


class NitterFetcher(BaseFetcher):

    def __init__(
        self,
        endpoint: str,
        client: HTTPClient,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.client = client

    def fetch(self, username: str) -> RawResponse:
        url = f"{self.endpoint}/{username}"

        return self.client.get(url)

    def fetch_rss(self, username: str) -> RawResponse:
        url = f"{self.endpoint}/{username}/rss"

        return self.client.get(url)
