import abc
from datetime import datetime
from typing import Self

from pydantic import BaseModel


class State(BaseModel, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def initial(cls) -> Self:
        pass


class BlueskyState(State):
    session: str | None
    last_post_id: str | None

    @classmethod
    def initial(cls) -> Self:
        return cls(
            session=None,
            last_post_id=None,
        )


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


class XcodeState(State):
    last_release_build: str | None

    @classmethod
    def initial(cls) -> Self:
        return cls(
            last_release_build=None,
        )
