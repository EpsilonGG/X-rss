from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from domain.models.author import Author
from domain.models.media import Media


class Tweet(BaseModel):

    tweet_id: str

    url: str

    content: str

    published: datetime

    author: Author

    media: list[Media] = Field(default_factory=list)
