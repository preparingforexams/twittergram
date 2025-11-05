import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterable

    from twittergram.application.model import RedditPost


class RedditReader(abc.ABC):
    @abc.abstractmethod
    def list_posts(self) -> AsyncIterable[RedditPost]:
        pass
