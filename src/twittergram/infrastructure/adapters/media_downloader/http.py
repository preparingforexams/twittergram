import logging
import mimetypes
import ssl
import uuid
from pathlib import Path

import aiofiles
import aiohttp
import certifi
from aiofiles.os import makedirs

from twittergram.application.exceptions.io import IoException
from twittergram.application.exceptions.media import UnsupportedMediaTypeException
from twittergram.application.ports import MediaDownloader
from twittergram.domain.model import MediaType, Medium
from twittergram.domain.value_objects import MediaFile

_LOG = logging.getLogger(__name__)


class HttpMediaDownloader(MediaDownloader):
    def __init__(self, directory: Path):
        self.directory = directory

    @staticmethod
    async def _session() -> aiohttp.ClientSession:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        return aiohttp.ClientSession(connector=connector)

    async def download(self, media: list[Medium]) -> list[MediaFile]:
        for medium in media:
            if medium.type != MediaType.PHOTO:
                raise UnsupportedMediaTypeException(
                    f"MediaType {medium.type} is not supported"
                )

        directory = self.directory / str(uuid.uuid4())
        await makedirs(directory)

        result: list[MediaFile] = []
        async with await self._session() as session:
            # TODO: we could utilize asyncio more here, but meh
            for medium in media:
                async with session.get(medium.url) as response:
                    match response.status:
                        case 200:
                            mime_type = response.content_type
                            extension = mimetypes.guess_extension(mime_type) or ""
                            path = directory / f"{medium.id}.{extension}"

                            async with aiofiles.open(path, "wb") as f:
                                await f.write(await response.read())

                            media_file = MediaFile(
                                medium=medium,
                                path=path,
                                mime_type=mime_type,
                            )
                            result.append(media_file)
                        case status_code if 400 <= status_code < 500:
                            _LOG.error(
                                "Received status code %d for URL %s. Skipping.",
                                response.status,
                                medium.url,
                            )
                        case status_code if 500 <= status_code < 600:
                            raise IoException(
                                "Received server error %d for URL %s",
                                status_code,
                                medium.url,
                            )

        return result
