from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class RawResponse:
    url: str
    status_code: int
    content_type: str
    text: str
    fetched_at: datetime
