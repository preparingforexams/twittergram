import asyncio
import logging
from pathlib import Path

from aiofiles.os import listdir as aio_listdir, makedirs as aio_makedirs  # type: ignore

from twittergram.application.exceptions.io import IoException
from twittergram.application.ports import TwitterDownloader
from twittergram.domain.model import Tweet

_LOG = logging.getLogger(__name__)


class GalleryDlTwitterDownloader(TwitterDownloader):
    def __init__(self, directory: Path):
        self.directory = directory

    async def download(self, tweet: Tweet) -> list[Path]:
        directory = self.directory / str(tweet.id)
        await aio_makedirs(directory, exist_ok=True)

        url = f"https://twitter.com/intent/status/{tweet.id}"
        process = await asyncio.create_subprocess_exec(
            "gallery-dl",
            "--directory",
            str(directory),
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

        return [directory / file for file in await aio_listdir(directory)]
