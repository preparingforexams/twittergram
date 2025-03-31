import logging
from dataclasses import dataclass
from datetime import datetime

from injector import inject

from twittergram.application import ports, repos
from twittergram.application.model import BlueskyPost, BlueskyState

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardBlueskyPosts:
    downloader: ports.MediaDownloader
    sanitizer: ports.HtmlSanitizer
    reader: ports.BlueskyReader
    state_repo: repos.StateRepo
    uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        state = await self.state_repo.load_state(BlueskyState)
        try:
            if session := state.session:
                self.reader.restore_session(session)

            _LOG.info("Reading posts")
            posts = await self._read_posts(state.last_post_id, state.last_post_time)

            if not posts:
                _LOG.info("No posts found")
                return

            # Reverse reverse chronological
            posts.reverse()

            _LOG.info("Forwarding %d posts", len(posts))

            for post in posts:
                await self._forward_post(post, state)
        finally:
            _LOG.debug("Extracting session from port")
            state.session = self.reader.save_session()
            _LOG.info("Storing state")
            await self.state_repo.store_state(state)

    async def _forward_post(self, post: BlueskyPost, state: BlueskyState) -> None:
        _LOG.info(
            "Processing post from %s (ID %s)",
            post.created_at,
            post.id,
        )
        if post.images:
            _LOG.info("Downloading images")
            media_files = await self.downloader.download(post.images)
        else:
            media_files = []
        _LOG.info("Sending message")

        is_html = False
        text = post.text

        if (url := post.url) is not None:
            is_html = True
            text = f"{text}\n\n{url.html_formatted()}"

        if media_files:
            await self.uploader.send_image_message(
                media_files,
                text,
                use_html=is_html,
            )
        elif text:
            await self.uploader.send_text_message(
                text,
                use_html=is_html,
            )
        else:
            _LOG.warning("Dropping post with neither image nor text")
        state.last_post_id = post.id
        state.last_post_time = post.created_at

    async def _read_posts(
        self,
        until_id: str | None,
        until_time: datetime | None,
    ) -> list[BlueskyPost]:
        posts: list[BlueskyPost] = []
        async for post in self.reader.list_posts():
            if post.id == until_id:
                break

            if until_time and post.created_at < until_time:
                _LOG.info(
                    "Last post probably deleted, found post with older creation time"
                )
                break

            posts.append(post)

            if until_id is None and len(posts) == 5:
                break

        return posts
