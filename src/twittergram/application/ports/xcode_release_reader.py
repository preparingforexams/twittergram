import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterable

    from twittergram.application.model import XcodeRelease


class XcodeReleaseReader(abc.ABC):
    @abc.abstractmethod
    def get_releases(self) -> AsyncIterable[XcodeRelease]:
        pass
