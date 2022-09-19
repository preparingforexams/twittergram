import abc
import logging
from pathlib import Path

from twittergram.domain.model import Tweet

_LOG = logging.getLogger(__name__)


class TwitterDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, tweet: Tweet) -> list[Path]:
        pass
