from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from domain.models.tweet import Tweet
from infrastructure.http import RawResponse


class BaseParser(ABC):
    @abstractmethod
    def parse(self, response: RawResponse) -> list[Tweet]:
        raise NotImplementedError
