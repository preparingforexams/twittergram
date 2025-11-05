from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from twittergram.application.model.media import Medium


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
