import abc
import logging
from collections.abc import AsyncIterable
from datetime import datetime

from twittergram.domain.model import Tweet

_LOG = logging.getLogger(__name__)


class TwitterReader(abc.ABC):
    @abc.abstractmethod
    async def lookup_user_id(self) -> int:
        pass

    @abc.abstractmethod
    def list_tweets(
        self, user_id: int, start_time: datetime, until_id: int | None = None
    ) -> AsyncIterable[Tweet]:
        pass
