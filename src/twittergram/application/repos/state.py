import abc

from twittergram.application.model import State


class StateRepo(abc.ABC):
    @abc.abstractmethod
    async def load_state[T: State](self, state_type: type[T]) -> T:
        pass

    @abc.abstractmethod
    async def store_state[T: State](self, state: T) -> None:
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        pass
