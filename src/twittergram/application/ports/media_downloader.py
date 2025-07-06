import abc
import logging

from twittergram.application.model import MediaFile, Medium

_LOG = logging.getLogger(__name__)


class MediaDownloader(abc.ABC):
    @abc.abstractmethod
    async def is_supported(self, medium: Medium) -> bool:
        pass

    @abc.abstractmethod
    async def download(self, medium: Medium) -> list[MediaFile]:
        pass
