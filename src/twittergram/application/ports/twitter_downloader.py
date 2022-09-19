import abc
import logging
from pathlib import Path

_LOG = logging.getLogger(__name__)


class TwitterDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, tweet_id: int) -> list[Path]:
        pass
