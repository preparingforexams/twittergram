from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import AsyncIterable

import tweepy
from tweepy.asynchronous import AsyncClient

from twittergram.config import TwitterConfig
from twittergram.io_exception import IoException


@dataclass
class Tweet:
    id: int

    @classmethod
    def from_data(cls, data: dict) -> Tweet:
        return cls(
            id=int(data["id"]),
        )


class TwitterReader:
    def __init__(self, config: TwitterConfig):
        self.api = AsyncClient(bearer_token=config.token)

    async def lookup_user_id(self, username: str) -> int:
        response: tweepy.Response = await self.api.get_user(username=username)
        if response.errors:
            raise IoException(f"Error from Twitter: {response.errors}")

        data: dict = response.data
        return int(data["id"])

    async def list_tweets(
        self,
        user_id: int,
        start_time: datetime.datetime,
        until_id: int | None = None

    ) -> AsyncIterable[Tweet]:
        paginator = tweepy.Paginator(
            method=self.api.get_users_tweets,
            id=user_id,
            max_results=100,
            since_id=until_id,
            end_time=start_time,
        )

        async for response in paginator.flatten():
            if response.errors:
                raise IoException(f"Error getting tweets: {response.errors}")

            yield Tweet.from_data(response.data)
