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
