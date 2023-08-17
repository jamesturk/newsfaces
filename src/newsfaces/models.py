from pydantic import BaseModel
from enum import Enum


class URL(BaseModel):
    url: str
    source: str


class ImageType(Enum):
    main = "main"
    social = "social"
    video_thumbnail = "video_thumbnail"


class Image(BaseModel):
    url: str
    image_type: ImageType
    caption: str = ""
    alt_text: str = ""


class Article(BaseModel):
    title: str
    article_text: str
    images: list[Image] = []
