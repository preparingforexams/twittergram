import asyncio
import logging
from typing import AsyncIterable, Iterable

import pendulum
from mastodon import Mastodon

from twittergram.application.exceptions.io import IoException
from twittergram.application.ports import MastodonReader
from twittergram.config import MastodonConfig
from twittergram.domain.model import Toot, Medium, MediaType

_LOG = logging.getLogger(__name__)


class MastodonPyMastodonReader(MastodonReader):
    def __init__(self, config: MastodonConfig):
        self.config = config

    @property
    def _client(self) -> Mastodon:
        return Mastodon(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            api_base_url=self.config.api_base_url,
        )

    def _lookup_user_id(self) -> int:
        client = self._client
        account_name = self.config.source_account
        account = client.account_lookup(account_name)
        if account is None:
            raise IoException(f"Could not look up user {account_name}")

        return account["id"]

    async def lookup_user_id(self) -> int:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._lookup_user_id)

    def _parse_media(self, media: list[dict]) -> list[Medium]:
        result: list[Medium] = []

        for m in media:
            medium = self._parse_medium(m)
            if medium:
                result.append(medium)

        return result

    @staticmethod
    def _parse_medium(m: dict) -> Medium | None:
        media_type: MediaType

        match m["type"]:
            case "image":
                media_type = MediaType.PHOTO
            case "video":
                media_type = MediaType.VIDEO
            case "gifv":
                media_type = MediaType.GIF
            case other:
                _LOG.warning("Unsupported media type %s", other)
                return None

        return Medium(
            id=str(["id"]),
            url=m["url"],
            type=media_type,
        )

    def _list_toots(
        self,
        user_id: int,
        until_id: int | None,
        limit: int | None,
    ) -> Iterable[Toot]:
        client = self._client
        statuses = client.account_statuses(
            user_id,
            exclude_replies=True,
            exclude_reblogs=True,
            since_id=until_id,
            limit=limit,
        )
        for status in statuses:
            yield Toot(
                id=status["id"],
                url=status["url"],
                content=status["content"],
                created_at=status["created_at"],
                media_attachments=self._parse_media(status["media_attachments"]),
            )

    async def list_toots(
        self,
        user_id: int,
        until_id: int | None = None,
    ) -> AsyncIterable[Toot]:
        limit = 10 if until_id is None else None

        loop = asyncio.get_running_loop()
        toots = await loop.run_in_executor(
            None, lambda: self._list_toots(user_id, until_id, limit)
        )
        for toot in toots:
            yield toot
