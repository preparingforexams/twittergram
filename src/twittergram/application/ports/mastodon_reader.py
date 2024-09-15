import abc
from collections.abc import AsyncIterable

from twittergram.domain.model import Toot


class MastodonReader(abc.ABC):
    @abc.abstractmethod
    async def lookup_user_id(self) -> int:
        pass

    @abc.abstractmethod
    def list_toots(
        self,
        user_id: int,
        until_id: int | None = None,
    ) -> AsyncIterable[Toot]:
        pass
