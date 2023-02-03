from dataclasses import dataclass
from datetime import datetime

from twittergram.domain.model.media import Medium


@dataclass(frozen=True)
class Toot:
    id: int
    url: str

    content: str | None
    """
    Content of the toot, as HTML
    """

    created_at: datetime
    media_attachments: list[Medium]
