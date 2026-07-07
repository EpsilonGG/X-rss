from pydantic import BaseModel


class Media(BaseModel):
    url: str
    type: str = "image"
