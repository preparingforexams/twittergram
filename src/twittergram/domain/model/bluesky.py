from dataclasses import dataclass
from datetime import datetime

from twittergram.domain.model.media import Medium


@dataclass(frozen=True)
class BlueskyPost:
    created_at: datetime
    id: str
    text: str | None
    images: list[Medium]
