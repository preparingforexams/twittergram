from dataclasses import dataclass
from datetime import datetime

from twittergram.domain.model.media import Medium


@dataclass(frozen=True, kw_only=True)
class NamedUrl:
    url: str
    title: str | None

    def html_formatted(self) -> str:
        title = self.title
        if title:
            return f'<a href="{self.url}">{title}</a>'
        else:
            return f'<a href="{self.url}">{self.url}</a>'


@dataclass(frozen=True, kw_only=True)
class BlueskyPost:
    created_at: datetime
    id: str
    text: str | None
    images: list[Medium]
    url: NamedUrl | None
