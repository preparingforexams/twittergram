from __future__ import annotations

import logging
from pathlib import Path

import aiofiles
import telegram

from twittergram.application.ports import TelegramUploader
from twittergram.config import TelegramConfig
from twittergram.domain.model import MediaType
from twittergram.domain.value_objects import MediaFile

_LOG = logging.getLogger(__name__)


class PtbTelegramUploader(TelegramUploader):
    def __init__(self, config: TelegramConfig):
        self.config = config

    async def _send_image(
        self,
        bot: telegram.Bot,
        chat_id: int,
        file_path: Path,
        caption: str | None,
    ) -> telegram.PhotoSize:
        async with aiofiles.open(file_path, "rb") as fd:
            input_file = telegram.InputFile(await fd.read())
            message = await bot.send_photo(
                chat_id=chat_id,
                photo=input_file,
                caption=caption,
                disable_notification=True,
                write_timeout=180,
            )
            return max(message.photo, key=lambda p: p.file_size)

    async def _send_video(
        self,
        bot: telegram.Bot,
        chat_id: int,
        file_path: Path,
        caption: str | None,
    ) -> telegram.Video:
        async with aiofiles.open(file_path, "rb") as fd:
            input_file = telegram.InputFile(await fd.read())
            message = await bot.send_video(
                chat_id=chat_id,
                video=input_file,
                caption=caption,
                disable_notification=True,
                write_timeout=180,
            )
            return message.video

    async def _create_items(
        self,
        bot: telegram.Bot,
        files: list[MediaFile],
    ) -> list[telegram.InputMediaPhoto | telegram.InputMediaVideo]:
        items: list[telegram.InputMediaPhoto | telegram.InputMediaVideo] = []
        chat_id = self.config.upload_chat
        for file in files:
            media_type = file.medium.type
            if media_type == MediaType.VIDEO:
                video = await self._send_video(bot, chat_id, file.path, caption=None)
                items.append(telegram.InputMediaVideo(media=video))
            elif media_type == MediaType.PHOTO:
                photo = await self._send_image(bot, chat_id, file.path, caption=None)
                items.append(telegram.InputMediaPhoto(photo))
            else:
                raise ValueError(f"Unknown media type {media_type}")

        return items

    async def send_text_message(self, text: str):
        async with telegram.Bot(token=self.config.token) as bot:
            await bot.send_message(
                chat_id=self.config.target_chat,
                disable_notification=True,
                text=text,
                write_timeout=180,
            )

    async def send_image_message(
        self, image_files: list[MediaFile], caption: str | None
    ):
        chat_id = self.config.target_chat

        async with telegram.Bot(token=self.config.token) as bot:
            if len(image_files) == 1:
                await self._send_image(bot, chat_id, image_files[0].path, caption)
            else:
                items = await self._create_items(bot, image_files)
                await bot.send_message(
                    chat_id,
                    caption,
                    disable_notification=True,
                    write_timeout=180,
                )
                await bot.send_media_group(
                    chat_id,
                    items,
                    disable_notification=True,
                    write_timeout=180,
                )
