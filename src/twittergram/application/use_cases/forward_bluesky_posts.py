import logging
from dataclasses import dataclass

from injector import inject

from twittergram.application import ports, repos
from twittergram.domain.model import BlueskyPost, BlueskyState

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
        until_id = state.last_post_id
        try:
            if session := state.session:
                self.reader.restore_session(session)

            _LOG.info("Reading posts")
            posts: list[BlueskyPost] = []
            async for post in self.reader.list_posts():
                if post.id == until_id:
                    break

                posts.append(post)

                if until_id is None and len(posts) == 5:
                    break

            if not posts:
                _LOG.info("No posts found")
                return

            # Reverse reverse chronological
            posts.reverse()

            _LOG.info("Forwarding %d posts", len(posts))

            for post in posts:
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
                if media_files:
                    await self.uploader.send_image_message(media_files, post.text)
                elif text := post.text:
                    await self.uploader.send_text_message(text)
                else:
                    _LOG.warning("Dropping post with neither image nor text")

                state.last_post_id = post.id
        finally:
            _LOG.debug("Extracting session from port")
            state.session = self.reader.save_session()
            _LOG.info("Storing state")
            await self.state_repo.store_state(state)
