import logging
import mimetypes
from asyncio import subprocess
from typing import TYPE_CHECKING

from httpx import URL

from twittergram.application.model import MediaFile, MediaType, Medium
from twittergram.application.ports import MediaDownloader

if TYPE_CHECKING:
    from pathlib import Path

_LOG = logging.getLogger(__name__)


class GalleryDlMediaDownloader(MediaDownloader):
    def __init__(self, directory: Path):
        self.directory = directory

    async def is_supported(self, medium: Medium) -> bool:
        if not medium.type == MediaType.PHOTO:
            return False

        url = URL(medium.url)
        if url.host == "www.reddit.com" and url.path.startswith("/gallery/"):
            return True

        return False

    async def download(self, medium: Medium) -> list[MediaFile]:
        if not await self.is_supported(medium):
            raise ValueError("Unsupported medium")
        download_dir = self.directory / medium.id
        gallery = await subprocess.create_subprocess_exec(
            "gallery-dl",
            "-w",
            f"-D={download_dir}",
            medium.url,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )

        _LOG.info("Waiting for gallery-dl on URL %s", medium.url)
        exit_code = await gallery.wait()

        if exit_code != 0:
            _LOG.error("gallery-dl failed with exit code %d", exit_code)
            return []

        files = sorted(download_dir.iterdir(), key=lambda it: it.name)
        result = []

        for file in files:
            mime_type, _ = mimetypes.guess_file_type(file)
            media_file = MediaFile(
                medium=medium,
                path=file,
                mime_type=mime_type or "",
            )
            result.append(media_file)

        return result
