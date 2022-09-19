import logging
from datetime import datetime
from typing import AsyncIterable

import tweepy
from tweepy.asynchronous import AsyncClient

from twittergram.application.exceptions.io import IoException
from twittergram.application.ports import TwitterReader
from twittergram.config import TwitterConfig
from twittergram.domain.model import Tweet

_LOG = logging.getLogger(__name__)


def _to_model(data: tweepy.Tweet) -> Tweet:
    return Tweet(
        id=int(data.id),
    )


class TweepyTwitterReader(TwitterReader):
    def __init__(self, config: TwitterConfig):
        self.api = AsyncClient(bearer_token=config.token)

    async def lookup_user_id(self, username: str) -> int:
        response: tweepy.Response = await self.api.get_user(username=username)
        if response.errors:
            raise IoException(f"Error from Twitter: {response.errors}")

        user: tweepy.User = response.data
        return user.id

    async def list_tweets(
        self, user_id: int, start_time: datetime, until_id: int | None = None
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

            data: list[tweepy.Tweet] = response.data or []
            for tweet_data in data:
                yield _to_model(tweet_data)

            page_token = response.meta.get("next_token")
            if not page_token:
                _LOG.debug("Stopping pagination because of missing next token")
                break
