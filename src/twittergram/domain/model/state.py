import abc
import dataclasses
from dataclasses import dataclass
from typing import Self, cast


class State(abc.ABC):
    @abc.abstractmethod
    def to_dict(self) -> dict[str, str | int | None]:
        pass

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, data: dict[str, str | int]) -> Self:
        pass


@dataclass
class MailState(State):
    mailbox_id: str | None

    def to_dict(self) -> dict[str, str | int | None]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str | int]) -> Self:
        return cls(
            mailbox_id=cast(str | None, data.get("mailbox_id")),
        )


@dataclass
class MastodonState(State):
    last_toot_id: int | None = None

    def to_dict(self) -> dict[str, str | int | None]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str | int]) -> Self:
        return cls(
            last_toot_id=cast(int | None, data.get("last_toot_id")),
        )


@dataclass
class TwitterState(State):
    last_tweet_id: int | None = None

    def to_dict(self) -> dict[str, str | int | None]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str | int]) -> Self:
        return cls(
            last_tweet_id=cast(int | None, data.get("last_tweet_id")),
        )
