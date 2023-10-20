import praw

from twittergram.application.ports import RedditReader
from twittergram.config import RedditConfig


class PrawRedditReader(RedditReader):
    def __init__(self, config: RedditConfig) -> None:
        self.reddit = praw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
        )

    async def lookup_user_id(self, name: str) -> str:
        redditor = self.reddit.redditor(name)
        return redditor.id
