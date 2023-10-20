from datetime import datetime, timezone
from typing import AsyncIterable

import asyncpraw

from twittergram.application.ports import RedditReader
from twittergram.config import RedditConfig
from twittergram.domain.model import URL, RedditPost


class PrawRedditReader(RedditReader):
    def __init__(self, config: RedditConfig) -> None:
        self.config = config

    @property
    def reddit(self) -> asyncpraw.Reddit:
        config = self.config
        return asyncpraw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
        )

    async def list_posts(self) -> AsyncIterable[RedditPost]:
        async with self.reddit as reddit:
            user = await reddit.redditor(self.config.source_username)
            async for submission in user.submissions.new():
                subreddit = submission.subreddit
                await subreddit.load()
                created_at = datetime.fromtimestamp(
                    submission.created_utc,
                    timezone.utc,
                )
                yield RedditPost(
                    id=submission.id,
                    created_at=created_at,
                    title=submission.title,
                    url=URL(submission.url),
                    subreddit_name=subreddit.display_name,
                )
