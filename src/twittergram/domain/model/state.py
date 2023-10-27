import abc
from datetime import datetime
from typing import Self

from pydantic import BaseModel


class State(BaseModel, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def initial(cls) -> Self:
        pass


class MailState(State):
    mailbox_id: str | None
    mailbox_state: str | None

    @classmethod
    def initial(cls) -> Self:
        return cls(mailbox_id=None, mailbox_state=None)


class MastodonState(State):
    last_toot_id: int | None

    @classmethod
    def initial(cls) -> Self:
        return cls(last_toot_id=None)


class RedditState(State):
    last_post_time: datetime | None

    @classmethod
    def initial(cls) -> Self:
        return cls(last_post_time=None)


class TwitterState(State):
    last_tweet_id: int | None

    @classmethod
    def initial(cls) -> Self:
        return cls(last_tweet_id=None)


class XcodeState(State):
    last_release_build: str | None

    @classmethod
    def initial(cls) -> Self:
        return cls(
            last_release_build=None,
        )
