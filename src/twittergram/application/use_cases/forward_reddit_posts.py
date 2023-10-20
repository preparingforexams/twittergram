import logging
from dataclasses import dataclass

from injector import inject

from twittergram.application import ports, repos

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardRedditPosts:
    state_repo: repos.StateRepo
    reddit_reader: ports.RedditReader
    telegram_uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        posts = self.reddit_reader.list_posts()
        async for post in posts:
            _LOG.info("First post: %s", post)
            break
