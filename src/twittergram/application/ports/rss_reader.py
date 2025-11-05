import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterable

    from twittergram.application.model import RssItem


class RssReader(abc.ABC):
    @abc.abstractmethod
    def list_items(self) -> AsyncIterable[RssItem]:
        pass
