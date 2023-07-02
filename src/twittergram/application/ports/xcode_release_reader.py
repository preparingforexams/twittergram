import abc
from typing import AsyncIterable

from twittergram.domain.model import XcodeRelease


class XcodeReleaseReader(abc.ABC):
    @abc.abstractmethod
    def get_releases(self) -> AsyncIterable[XcodeRelease]:
        pass
