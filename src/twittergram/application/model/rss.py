from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from .url import URL


@dataclass(frozen=True, kw_only=True)
class RssItem:
    id: str
    title: str
    links: list[URL]
    published_at: datetime
    synopsis: str | None
