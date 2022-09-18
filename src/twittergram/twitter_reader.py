from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import AsyncIterable

import tweepy
from tweepy.asynchronous import AsyncClient

from twittergram.config import TwitterConfig
from twittergram.io_exception import IoException

_LOG = logging.getLogger(__name__)


@dataclass
class Tweet:
    id: int

    @classmethod
    def from_data(cls, data: tweepy.Tweet) -> Tweet:
        return cls(
            id=int(data.id),
        )


class TwitterReader:
    def __init__(self, config: TwitterConfig):
        self.api = AsyncClient(bearer_token=config.token)

    async def lookup_user_id(self, username: str) -> int:
        response: tweepy.Response = await self.api.get_user(username=username)
        if response.errors:
            raise IoException(f"Error from Twitter: {response.errors}")

        user: tweepy.User = response.data
        return user.id

    async def list_tweets(
        self, user_id: int, start_time: datetime.datetime, until_id: int | None = None
    ) -> AsyncIterable[Tweet]:
        async def _get_tweets(pagination_token: str | None) -> tweepy.Response:
            return await self.api.get_users_tweets(
                id=user_id,
                max_results=100,
                since_id=until_id,
                end_time=start_time,
                pagination_token=pagination_token,
            )

        page_token: str | None = None
        while True:
            _LOG.debug("Loading next page of tweets")
            response = await _get_tweets(page_token)
            if response.errors:
                raise IoException(f"Error getting tweets: {response.errors}")

            for tweet_data in response.data:
                yield Tweet.from_data(tweet_data)

            page_token = response.meta.get("next_token")
            if not page_token:
                _LOG.debug("Stopping pagination because of missing next token")
                break
