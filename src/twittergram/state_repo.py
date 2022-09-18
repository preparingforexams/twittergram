import abc
import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path

from aiofiles import open as aio_open
from aiofiles.os import path as aio_path


@dataclass
class State:
    last_tweet_id: int | None


class StateRepo(abc.ABC):
    @abc.abstractmethod
    async def load_state(self) -> State | None:
        pass

    @abc.abstractmethod
    async def store_state(self, state: State):
        pass


class FileStateRepo(StateRepo):
    def __init__(self, path: Path):
        self.path = path

    async def load_state(self) -> State | None:
        if not await aio_path.isfile(self.path):
            return None

        async with aio_open(self.path) as f:
            content = await f.read()
            data = json.loads(content)
            return State(**data)

    async def store_state(self, state: State):
        async with aio_open(self.path, "w") as f:
            content = json.dumps(dataclasses.asdict(state))
            await f.write(content)
