import logging
import mimetypes
import uuid
from typing import TYPE_CHECKING

import aiofiles
from aiofiles.os import makedirs
from httpx import URL, AsyncClient

from twittergram.application.exceptions.io import IoException
from twittergram.application.exceptions.media import UnsupportedMediaTypeException
from twittergram.application.model import MediaFile, MediaType, Medium
from twittergram.application.ports import MediaDownloader

if TYPE_CHECKING:
    from pathlib import Path

_LOG = logging.getLogger(__name__)


class HttpMediaDownloader(MediaDownloader):
    def __init__(self, directory: Path):
        self.directory = directory
        self._session = AsyncClient(
            timeout=120,
            follow_redirects=True,
        )

    async def is_supported(self, medium: Medium) -> bool:
        if not medium.type == MediaType.PHOTO:
            return False

        url = URL(medium.url)
        if url.host == "www.reddit.com" and url.path.startswith("/gallery/"):
            return False

        return True

    async def download(self, medium: Medium) -> list[MediaFile]:
        if medium.type != MediaType.PHOTO:
            raise UnsupportedMediaTypeException(
                f"MediaType {medium.type} is not supported"
            )

        directory = self.directory / str(uuid.uuid4())
        await makedirs(directory)

        result: list[MediaFile] = []

        response = await self._session.get(medium.url)
        match response.status_code:
            case 200:
                mime_type = response.headers.get("Content-Type")
                extension = mimetypes.guess_extension(mime_type) or ""
                path = directory / f"{medium.id}.{extension}"

                async with aiofiles.open(path, "wb") as f:
                    await f.write(response.content)

                media_file = MediaFile(
                    medium=medium,
                    path=path,
                    mime_type=mime_type,
                )
                result.append(media_file)
            case status_code if 400 <= status_code < 500:
                _LOG.error(
                    "Received status code %d for URL %s. Skipping.",
                    status_code,
                    medium.url,
                )
            case status_code if 500 <= status_code < 600:
                raise IoException(
                    "Received server error %d for URL %s",
                    status_code,
                    medium.url,
                )

        return result
