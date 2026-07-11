from pathlib import Path

from pydantic import BaseModel


class HTTPConfig(BaseModel):
    timeout: int = 20


class ProviderConfig(BaseModel):
    endpoints: list[str]


class RSSConfig(BaseModel):
    output: str = "feed/"

    @property
    def output_path(self) -> Path:
        return Path(self.output)


class RSSConfig(BaseModel):
    output: str = "feeds/"
    processed_output: str = "feeds_processed/"

    @property
    def output_path(self) -> Path:
        return Path(self.output)

    @property
    def processed_output_path(self) -> Path:
        return Path(self.processed_output)
