import logging
from dataclasses import dataclass

from injector import inject

from twittergram.application import ports, repos
from twittergram.config import RedditConfig
from twittergram.domain.model import MediaType, Medium, RedditPost, RedditState

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardRedditPosts:
    config: RedditConfig
    media_downloader: ports.MediaDownloader
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

            if last_post_time is None and len(posts) == 5:
                break

            if last_post_time is not None and post.created_at <= last_post_time:
                break

        if not posts:
            _LOG.info("No posts found")
            return

        # We want to forward post them in reverse order
        posts.reverse()

        _LOG.info("Downloading media")
        media = [
            Medium(type=MediaType.PHOTO, id=post.id, url=str(post.url))
            for post in posts
        ]
        media_files = await self.media_downloader.download(media)

        media_file_by_post_id = {file.medium.id: file for file in media_files}

        _LOG.info("Forwarding %d posts", len(posts))
        try:
            for post in posts:
                await self.telegram_uploader.send_image_message(
                    image_files=[media_file_by_post_id[post.id]],
                    caption=post.title,
                )
                state.last_post_time = post.created_at
        finally:
            _LOG.debug("Storing state")
            await self.state_repo.store_state(state)
