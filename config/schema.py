from pathlib import Path

from pydantic import BaseModel


class HTTPConfig(BaseModel):
    timeout: int = 20


class ProviderConfig(BaseModel):
    endpoints: list[str]


class RSSConfig(BaseModel):
    output: str = "output/feeds/"
    processed_output: str = "output/feeds_processed/"

    @property
    def output_path(self) -> Path:
        return Path(self.output)

    @property
    def processed_output_path(self) -> Path:
        return Path(self.processed_output)


class Config(BaseModel):
    provider: ProviderConfig
    http: HTTPConfig
    rss: RSSConfig
