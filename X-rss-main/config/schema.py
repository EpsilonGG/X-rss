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


class Config(BaseModel):

    provider: ProviderConfig

    http: HTTPConfig

    rss: RSSConfig
