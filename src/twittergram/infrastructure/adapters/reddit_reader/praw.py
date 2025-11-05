from datetime import UTC, datetime
from typing import TYPE_CHECKING

import asyncpraw

from twittergram.application.model import URL, RedditPost
from twittergram.application.ports import RedditReader

if TYPE_CHECKING:
    from collections.abc import AsyncIterable

    from twittergram.config import RedditConfig


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
            check_for_updates=False,
        )

    async def list_posts(self) -> AsyncIterable[RedditPost]:
        async with self.reddit as reddit:
            user = await reddit.redditor(self.config.source_username)
            async for submission in user.submissions.new():
                subreddit = submission.subreddit
                await subreddit.load()
                created_at = datetime.fromtimestamp(
                    submission.created_utc,
                    UTC,
                )
                yield RedditPost(
                    id=submission.id,
                    created_at=created_at,
                    title=submission.title,
                    url=URL(submission.url),
                    subreddit_name=subreddit.display_name,
                )
