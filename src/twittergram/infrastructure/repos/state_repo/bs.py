from asyncio import Lock
from collections.abc import Awaitable, Callable
from typing import Any, cast

from bs_state import StateStorage

from twittergram.application.model import State
from twittergram.application.repos import StateRepo
from twittergram.application.repos.state import T

type StorageLoader = Callable[[State], Awaitable[StateStorage[State]]]


class BsStateRepo(StateRepo):
    def __init__(self, storage_loader: StorageLoader):
        self._storages_lock = Lock()
        self._storages: dict[type, StateStorage[Any]] = {}
        self.storage_loader = storage_loader

    async def _load_storage(self, state_type: type[T]) -> StateStorage[T]:
        return cast(StateStorage[T], await self.storage_loader(state_type.initial()))

    async def _get_storage(self, state_type: type[T]) -> StateStorage[T]:
        storage = cast(StateStorage[T] | None, self._storages.get(state_type))

        if storage is not None:
            return storage

        async with self._storages_lock:
            storage = cast(StateStorage[T] | None, self._storages.get(state_type))

            if storage is None:
                storage = await self._load_storage(state_type)
                self._storages[state_type] = storage

            return storage

    async def load_state(self, state_type: type[T]) -> T:
        storage = await self._get_storage(state_type)
        return await storage.load()

    async def store_state(self, state: State) -> None:
        storage = await self._get_storage(type(state))
        await storage.store(state)
