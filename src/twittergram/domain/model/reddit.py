from dataclasses import dataclass
from datetime import datetime

from .url import URL


@dataclass(frozen=True)
class RedditPost:
    id: str
    created_at: datetime
    title: str
    url: URL
    subreddit_name: str
