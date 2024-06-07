import abc
from typing import AsyncIterable

from twittergram.domain.model import BlueskyPost


class BlueskyReader(abc.ABC):
    @abc.abstractmethod
    def save_session(self) -> str | None:
        pass

    @abc.abstractmethod
    def restore_session(self, session: str) -> None:
        pass

    @abc.abstractmethod
    def list_posts(self) -> AsyncIterable[BlueskyPost]:
        pass
