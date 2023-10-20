import logging
from dataclasses import dataclass

from injector import inject

from twittergram.application import ports, repos
from twittergram.config import RedditConfig
from twittergram.domain.model import RedditPost, RedditState

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardRedditPosts:
    config: RedditConfig
    reddit_reader: ports.RedditReader
    state_repo: repos.StateRepo
    telegram_uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        _LOG.debug("Loading state")
        state = await self.state_repo.load_state(RedditState)
        last_post_time = state.last_post_time

        _LOG.info("Fetching posts")
        subreddit_filter = self.config.subreddit_filter
        posts: list[RedditPost] = []
        async for post in self.reddit_reader.list_posts():
            if subreddit_filter is not None and post.subreddit_name == subreddit_filter:
                posts.append(post)

            if last_post_time is None or post.created_at <= last_post_time:
                break

        # We want to forward post them in reverse order
        posts.reverse()

        try:
            for post in posts:
                _LOG.info("Would forward %s", post.title)

        finally:
            await self.state_repo.store_state(state)
