import logging
from dataclasses import dataclass

from injector import inject

from twittergram.application import ports, repos
from twittergram.application.model import (
    MediaFile,
    MediaType,
    Medium,
    RedditPost,
    RedditState,
)
from twittergram.config import RedditConfig

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardRedditPosts:
    config: RedditConfig
    media_downloader: list[ports.MediaDownloader]
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
            if last_post_time is not None and post.created_at <= last_post_time:
                break

            if subreddit_filter is not None and post.subreddit_name == subreddit_filter:
                posts.append(post)

            if last_post_time is None and len(posts) == 5:
                break

        if not posts:
            _LOG.info("No posts found")
            return

        # We want to forward post them in reverse order
        posts.reverse()

        _LOG.info("Downloading media")
        media_files_by_post_id: dict[str, list[MediaFile]] = {}
        for post in posts:
            medium = Medium(type=MediaType.PHOTO, id=post.id, url=str(post.url))
            for downloader in self.media_downloader:
                if not await downloader.is_supported(medium):
                    continue

                media_files = await downloader.download(medium)
                media_files_by_post_id[post.id] = media_files
                break
            else:
                _LOG.warning("No downloader supports %s", medium)
                media_files_by_post_id[post.id] = []

        _LOG.info("Forwarding %d posts", len(posts))
        try:
            for post in posts:
                media_files = media_files_by_post_id[post.id]
                if media_files:
                    await self.telegram_uploader.send_documents_message(
                        documents=media_files,
                        caption=post.title,
                    )
                state.last_post_time = post.created_at
        finally:
            _LOG.debug("Storing state")
            await self.state_repo.store_state(state)
