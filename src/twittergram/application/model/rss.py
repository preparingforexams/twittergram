from dataclasses import dataclass
from datetime import datetime

from .url import URL


@dataclass(frozen=True, kw_only=True)
class RssItem:
    id: str
    title: str
    links: list[URL]
    published_at: datetime
    synopsis: str | None
