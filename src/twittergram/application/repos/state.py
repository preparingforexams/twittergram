import abc

from twittergram.domain.model import State


class StateRepo(abc.ABC):
    @abc.abstractmethod
    async def load_state(self) -> State | None:
        pass

    @abc.abstractmethod
    async def store_state(self, state: State):
        pass
