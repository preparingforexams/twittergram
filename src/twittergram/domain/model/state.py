import abc
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import Self, TypeAlias, cast

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
    mailbox_state: str | None

    def to_dict(self) -> dict[str, JsonSerializable]:
        return dataclasses.asdict(self)

    @classmethod
    def initial(cls) -> Self:
        return cls(None, None)

    @classmethod
    def from_dict(cls, data: dict[str, JsonSerializable]) -> Self:
        return cls(
            mailbox_id=cast(str | None, data.get("mailbox_id")),
            mailbox_state=cast(str | None, data.get("mailbox_state")),
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
class RedditState(State):
    last_post_time: datetime | None

    def to_dict(self) -> dict[str, JsonSerializable]:
        if (last_post_time := self.last_post_time) is not None:
            return {"last_post_time": last_post_time.isoformat()}

        return {}

    @classmethod
    def initial(cls) -> Self:
        return cls(None)

    @classmethod
    def from_dict(cls, data: dict[str, JsonSerializable]) -> Self:
        if last_post_time := data.get("last_post_time"):
            return cls(
                last_post_time=datetime.fromisoformat(cast(str, last_post_time)),
            )

        return cls.initial()


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


@dataclass
class XcodeState(State):
    last_release_build: str | None

    def to_dict(self) -> dict[str, JsonSerializable]:
        return dataclasses.asdict(self)

    @classmethod
    def initial(cls) -> Self:
        return cls(
            last_release_build=None,
        )

    @classmethod
    def from_dict(cls, data: dict[str, JsonSerializable]) -> Self:
        return cls(
            last_release_build=cast(str | None, data.get("last_release_build")),
        )
