import json
from pathlib import Path

from aiofiles import open as aio_open
from aiofiles.os import path as aio_path

from twittergram.application.repos import StateRepo
from twittergram.application.repos.state import T
from twittergram.domain.model import State


class FileStateRepo(StateRepo):
    def __init__(self, path: Path):
        self.path = path

    async def load_state(self, state_type: type[T]) -> T:
        if not await aio_path.isfile(self.path):
            return state_type.initial()

        async with aio_open(self.path) as f:
            content = await f.read()
            data = json.loads(content)
            return state_type.from_dict(data)

    async def store_state(self, state: State):
        async with aio_open(self.path, "w") as f:
            content = json.dumps(state.to_dict())
            await f.write(content)
