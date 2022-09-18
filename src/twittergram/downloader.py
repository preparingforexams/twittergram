import asyncio
import logging
from pathlib import Path

from aiofiles.os import listdir as aio_listdir  # type: ignore

from twittergram.io_exception import IoException

_LOG = logging.getLogger(__name__)


class Downloader:
    def __init__(self, directory: Path):
        self.directory = directory

    async def download(self, tweet_id: int) -> list[Path]:
        url = f"https://twitter.com/intent/status/{tweet_id}"
        process = await asyncio.create_subprocess_exec(
            "gallery-dl",
            "--directory",
            str(self.directory),
            url,
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if stderr:
            _LOG.warning("Warning output from gallery-dl: %s", stderr)

        if stdout:
            _LOG.debug("Stdout from gallery-dl: %s", stdout)

        if process.returncode:
            _LOG.error(
                "gallery-dl returned with code %d for URL %s",
                process.returncode,
                url,
            )
            raise IoException("Could not download tweet")

        return [Path(file) for file in await aio_listdir(self.directory)]
