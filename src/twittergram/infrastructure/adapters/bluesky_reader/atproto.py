import logging
from collections.abc import AsyncIterable
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from atproto import AsyncClient
from atproto.exceptions import BadRequestError
from atproto_client.models.app.bsky.embed.external import Main as ExternalEmbed
from atproto_client.models.app.bsky.embed.images import Main as ImageEmbed

from twittergram.application.exceptions.io import IoException
from twittergram.application.model import URL, BlueskyPost, MediaType, Medium, NamedUrl
from twittergram.application.ports import BlueskyReader
from twittergram.config import BlueskyConfig

_LOG = logging.getLogger(__name__)


class AtprotoBlueskyReader(BlueskyReader):
    BLOB_URL = URL("https://bsky.social/xrpc/com.atproto.sync.getBlob")

    def __init__(self, config: BlueskyConfig) -> None:
        self.config = config
        self.session: str | None = None

    def restore_session(self, session: str) -> None:
        self.session = session

    def save_session(self) -> str | None:
        return self.session

    @asynccontextmanager
    async def client(self) -> AsyncClient:
        client = AsyncClient()
        session = self.session

        if session is not None:
            try:
                await client.login(session_string=session)
            except BadRequestError as e:
                if e.response.content.error == "ExpiredToken":
                    _LOG.warning("Bluesky session expired")
                    self.session = session = None
                    client = AsyncClient()
                else:
                    raise IoException("Unexpected error during session login") from e

        if session is None:
            await client.login(login=self.config.user, password=self.config.password)
            self.session = client.export_session_string()

        try:
            yield client
        finally:
            _LOG.info("Exporting session")
            self.session = client.export_session_string()

    async def list_posts(self) -> AsyncIterable[BlueskyPost]:
        async with self.client() as client:
            assert isinstance(client, AsyncClient)
            initial_loop = True
            cursor: str | None = None
            while initial_loop or cursor is not None:
                initial_loop = False
                response = await client.get_author_feed(
                    actor=self.config.author_id,
                    limit=50,
                    filter="posts_no_replies",
                    cursor=cursor,
                )
                cursor = response.cursor

                for feed_post_view in response.feed:
                    post_view = feed_post_view.post
                    did = post_view.author.did
                    record = post_view.record

                    text = record.text or None

                    created_at = datetime.fromisoformat(record.created_at)

                    post = BlueskyPost(
                        created_at=created_at,
                        id=post_view.cid,
                        text=text,
                        images=self._extract_images(did, record.embed),
                        url=self._extract_url(record.embed),
                    )

                    yield post

    @classmethod
    def _extract_images(cls, did: str, embed: Any) -> list[Medium]:
        if isinstance(embed, ImageEmbed):
            return [
                cls._create_image_medium(
                    did=did,
                    cid=image.image.cid.encode(),
                )
                for image in embed.images
            ]

        return []

    @staticmethod
    def _extract_url(embed: Any) -> NamedUrl | None:
        if isinstance(embed, ExternalEmbed):
            external = embed.external
            return NamedUrl(
                title=external.title,
                url=external.uri,
            )

        return None

    @classmethod
    def _create_image_medium(cls, did: str, cid: str) -> Medium:
        url = cls.BLOB_URL.copy_set_param("cid", cid).copy_set_param("did", did)
        return Medium(
            url=str(url),
            id=cid,
            type=MediaType.PHOTO,
        )
