from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from pathlib import Path

from domain.models.tweet import Tweet


class BaseExporter(ABC):
    @abstractmethod
    def export(
        self,
        tweets: list[Tweet],
        *,
        output_path: Path,
        title: str,
        link: str,
        description: str,
    ) -> None:
        raise NotImplementedError
