from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from infrastructure.http import RawResponse


class BaseFetcher(ABC):

    @abstractmethod
    def fetch(self, username: str) -> RawResponse:
        raise NotImplementedError
