from collections import deque


class EndpointPool:
    def __init__(self, endpoints: list[str]) -> None:
        self._endpoints = deque(endpoints)

    def endpoints(self) -> list[str]:
        return list(self._endpoints)

    def mark_success(self, endpoint: str) -> None:
        while self._endpoints[0] != endpoint:
            self._endpoints.rotate(-1)

    def mark_failure(self, endpoint: str) -> None:
        if self._endpoints[0] == endpoint:
            self._endpoints.rotate(-1)
