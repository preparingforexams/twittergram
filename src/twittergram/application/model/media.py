from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class MediaType(Enum):
    VIDEO = "video"
    PHOTO = "photo"
    GIF = "animated_gif"


@dataclass(frozen=True)
class Medium:
    type: MediaType
    id: str
    url: str


@dataclass(frozen=True)
class MediaFile:
    medium: Medium
    path: Path
    mime_type: str
