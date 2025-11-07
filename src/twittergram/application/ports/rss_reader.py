import abc
from collections.abc import AsyncIterable

from twittergram.application.model import RssItem


class RssReader(abc.ABC):
    @abc.abstractmethod
    def list_items(self) -> AsyncIterable[RssItem]:
        pass
