from dataclasses import dataclass
from enum import Enum


class MediaType(Enum):
    VIDEO = "video"
    PHOTO = "photo"
    GIF = "animated_gif"


@dataclass(frozen=True)
class Medium:
    type: MediaType
    key: str
    url: str


@dataclass(frozen=True)
class Attachments:
    media: list[Medium]


@dataclass(frozen=True)
class Tweet:
    id: int
    text: str | None
    attachments: Attachments
