import abc
import dataclasses
from dataclasses import dataclass
from typing import Self, cast, TypeAlias

JsonSerializable: TypeAlias = (
    str | int | None | list["JsonSerializable"] | dict[str, "JsonSerializable"]
)


class State(abc.ABC):
    @abc.abstractmethod
    def to_dict(self) -> dict[str, JsonSerializable]:
        pass

    @classmethod
    @abc.abstractmethod
    def initial(cls) -> Self:
        pass

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, data: dict[str, JsonSerializable]) -> Self:
        pass


@dataclass
class MailState(State):
    mailbox_id: str | None

    def to_dict(self) -> dict[str, JsonSerializable]:
        return dataclasses.asdict(self)

    @classmethod
    def initial(cls) -> Self:
        return cls(None)

    @classmethod
    def from_dict(cls, data: dict[str, JsonSerializable]) -> Self:
        return cls(
            mailbox_id=cast(str | None, data.get("mailbox_id_by_name")),
        )


@dataclass
class MastodonState(State):
    last_toot_id: int | None

    def to_dict(self) -> dict[str, JsonSerializable]:
        return dataclasses.asdict(self)

    @classmethod
    def initial(cls) -> Self:
        return cls(None)

    @classmethod
    def from_dict(cls, data: dict[str, JsonSerializable]) -> Self:
        return cls(
            last_toot_id=cast(int | None, data.get("last_toot_id")),
        )


@dataclass
class TwitterState(State):
    last_tweet_id: int | None

    def to_dict(self) -> dict[str, JsonSerializable]:
        return dataclasses.asdict(self)

    @classmethod
    def initial(cls) -> Self:
        return cls(None)

    @classmethod
    def from_dict(cls, data: dict[str, JsonSerializable]) -> Self:
        return cls(
            last_tweet_id=cast(int | None, data.get("last_tweet_id")),
        )
