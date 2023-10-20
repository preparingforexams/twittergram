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
        user_id = await self.reddit_reader.lookup_user_id("schneckedertzchen")
        _LOG.info("Found user ID: %s", user_id)
