from dataclasses import dataclass
from pathlib import Path

from twittergram.domain.model import Medium


@dataclass(frozen=True)
class MediaFile:
    medium: Medium
    path: Path
    mime_type: str
