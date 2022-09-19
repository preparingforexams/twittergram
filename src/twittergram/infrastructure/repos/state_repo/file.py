import dataclasses
import json
from pathlib import Path

from aiofiles import open as aio_open
from aiofiles.os import path as aio_path

from twittergram.application.repos import StateRepo
from twittergram.domain.model import State


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
