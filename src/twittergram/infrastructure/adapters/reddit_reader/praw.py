import asyncpraw

from twittergram.application.ports import RedditReader
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
        )

    async def lookup_user_id(self, name: str) -> str:
        async with self.reddit as reddit:
            redditor = await reddit.redditor(name, fetch=True)
            return redditor.id
