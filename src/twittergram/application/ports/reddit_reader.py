import abc
from typing import AsyncIterable

from twittergram.domain.model import RedditPost


class RedditReader(abc.ABC):
    @abc.abstractmethod
    def list_posts(self) -> AsyncIterable[RedditPost]:
        pass
