import abc
from typing import TypeVar

from twittergram.application.model import State

T = TypeVar("T", bound=State)


class StateRepo(abc.ABC):
    @abc.abstractmethod
    async def load_state(self, state_type: type[T]) -> T:
        pass

    @abc.abstractmethod
    async def store_state(self, state: T) -> None:
        pass
