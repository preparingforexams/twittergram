import abc
import logging

from twittergram.domain.model import Medium
from twittergram.domain.value_objects import MediaFile

_LOG = logging.getLogger(__name__)


class TwitterDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, media: list[Medium]) -> list[MediaFile]:
        pass
