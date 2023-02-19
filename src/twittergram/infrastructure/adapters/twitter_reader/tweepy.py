import logging
from datetime import datetime
from typing import AsyncIterable, cast

import tweepy
from tweepy.asynchronous import AsyncClient, AsyncPaginator
from tweepy.client import Response

from twittergram.application.exceptions.io import IoException
from twittergram.application.ports import TwitterReader
from twittergram.config import TwitterConfig
from twittergram.domain.model import Tweet, MediaType, TweetAttachments, Medium

_LOG = logging.getLogger(__name__)


def _media_to_model(data: tweepy.Media) -> Medium:
    return Medium(
        id=data.media_key,
        type=MediaType(data.type),
        url=data.url,
    )


def _to_model(data: tweepy.Tweet, media: dict[str, Medium]) -> Tweet:
    attachments = data.attachments or {}
    media_keys = attachments.get("media_keys", [])
    return Tweet(
        id=int(data.id),
        # Make empty strings None
        text=data.text or None,
        attachments=TweetAttachments(
            media=[media[media_key] for media_key in media_keys],
        ),
    )


class TweepyTwitterReader(TwitterReader):
    def __init__(self, config: TwitterConfig) -> None:
        self.api = AsyncClient(bearer_token=config.token)
        self._username = config.source_account

    async def lookup_user_id(self) -> int:
        response: tweepy.Response = await self.api.get_user(username=self._username)
        if response.errors:
            raise IoException(f"Error from Twitter: {response.errors}")

        user: tweepy.User = response.data
        return cast(int, user.id)

    async def list_tweets(
        self, user_id: int, start_time: datetime, until_id: int | None = None
    ) -> AsyncIterable[Tweet]:
        responses: AsyncIterable[Response] = AsyncPaginator(
            self.api.get_users_tweets,
            id=user_id,
            expansions=["attachments.media_keys"],
            media_fields=["url", "type", "media_key"],
            exclude=["replies", "retweets"],
            since_id=until_id,
            end_time=start_time,
            max_results=100,
        )

        async for response in responses:
            if response.errors:
                raise IoException(f"Error getting tweets: {response.errors}")

            data: list[tweepy.Tweet] = response.data or []
            media: list[tweepy.Media] = response.includes.get("media", [])
            media_by_key = {
                medium.media_key: _media_to_model(medium) for medium in media
            }

            for tweet_data in data:
                yield _to_model(tweet_data, media_by_key)
