import logging
import uuid
from pathlib import Path

import aiofiles
import aiohttp
from aiofiles.os import makedirs

from twittergram.application.exceptions.media import UnsupportedMediaTypeException
from twittergram.application.ports import MediaDownloader
from twittergram.domain.model import Medium, MediaType
from twittergram.domain.value_objects import MediaFile

_LOG = logging.getLogger(__name__)


class HttpMediaDownloader(MediaDownloader):
    def __init__(self, directory: Path):
        self.directory = directory

    async def download(self, media: list[Medium]) -> list[MediaFile]:
        for medium in media:
            if medium.type != MediaType.PHOTO:
                raise UnsupportedMediaTypeException(
                    f"MediaType {medium.type} is not supported"
                )

        directory = self.directory / str(uuid.uuid4())
        await makedirs(directory)

        result: list[MediaFile] = []
        async with aiohttp.ClientSession() as session:
            # TODO: we could utilize asyncio more here, but meh
            for medium in media:
                async with session.get(medium.url) as response:
                    if response.status == 200:
                        path = directory / medium.key

                        async with aiofiles.open(path, "wb") as f:
                            await f.write(await response.read())

                        media_file = MediaFile(
                            medium=medium,
                            path=path,
                            mime_type=response.content_type,
                        )
                        result.append(media_file)

        return result
