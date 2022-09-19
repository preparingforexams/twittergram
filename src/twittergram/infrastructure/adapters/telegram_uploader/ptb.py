import asyncio
import logging
import mimetypes
from enum import Enum, auto
from pathlib import Path

import aiofiles
import telegram
from more_itertools import chunked

from twittergram.application.exceptions.io import IoException
from twittergram.application.ports import TelegramUploader
from twittergram.config import TelegramConfig

_LOG = logging.getLogger(__name__)


class MediaType(Enum):
    photo = auto()
    video = auto()


class PtbTelegramUploader(TelegramUploader):
    def __init__(self, config: TelegramConfig):
        self.config = config

    @staticmethod
    def _determine_type(
        file: Path,
    ) -> tuple[Path, MediaType]:
        mimetype, _ = mimetypes.guess_type(file)
        if not mimetype:
            raise IoException(f"Could not guess mimetype of file {file}")

        if mimetype.startswith("video/"):
            return file, MediaType.video

        if mimetype.startswith("image/"):
            return file, MediaType.photo

        raise ValueError(f"Unsupported mime type {mimetype} for file {file}")

    async def _create_items(
        self,
        bot: telegram.Bot,
        files: list[Path],
    ) -> list[telegram.InputMediaPhoto | telegram.InputMediaVideo]:
        loop = asyncio.get_running_loop()

        futures = [
            loop.run_in_executor(
                None,
                self._determine_type,
                file,
            )
            for file in files
        ]

        done, _ = await asyncio.wait(futures)

        type_by_file = {}
        for task in done:
            file, media_type = task.result()
            type_by_file[file] = media_type

        items: list[telegram.InputMediaPhoto | telegram.InputMediaVideo] = []
        chat_id = self.config.upload_chat
        for file, media_type in type_by_file.items():
            async with aiofiles.open(file, "rb") as fd:
                input_file = telegram.InputFile(await fd.read())
                if media_type == MediaType.video:
                    message = await bot.send_video(chat_id=chat_id, video=input_file)
                    items.append(telegram.InputMediaVideo(message.video))
                elif media_type == MediaType.photo:
                    message = await bot.send_photo(chat_id=chat_id, photo=input_file)
                    largest_photo = max(message.photo, key=lambda p: p.file_size)
                    items.append(telegram.InputMediaPhoto(largest_photo))
                else:
                    raise ValueError(f"Unknown media type {media_type}")

        return items

    async def upload_media(self, media_files: list[Path]):
        chat_id = self.config.target_chat
        async with telegram.Bot(token=self.config.token) as bot:
            for chunk in chunked(media_files, n=10):
                items = await self._create_items(bot, chunk)

                await bot.send_media_group(
                    chat_id=chat_id,
                    media=items,
                    disable_notification=True,
                )
