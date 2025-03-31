import abc
import logging

from twittergram.application.model import MediaFile, Medium

_LOG = logging.getLogger(__name__)


class MediaDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, media: list[Medium]) -> list[MediaFile]:
        pass
