import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import timedelta
from pathlib import Path
from typing import cast

import aiofiles
import telegram
from telegram import InputMediaDocument
from telegram.constants import ParseMode
from telegram.error import RetryAfter

from twittergram.application.model import MediaFile, MediaType
from twittergram.application.ports import TelegramUploader
from twittergram.config import TelegramConfig

_LOG = logging.getLogger(__name__)


async def _auto_retry[T](func: Callable[[], Awaitable[T]]) -> T:
    try:
        return await func()
    except RetryAfter as e:
        _LOG.debug(
            "Received RetryAfter exception, waiting for %d seconds",
            e.retry_after,
        )
        retry_after = cast(timedelta, e.retry_after)
        await asyncio.sleep(retry_after.total_seconds())

    return await func()


class PtbTelegramUploader(TelegramUploader):
    def __init__(self, config: TelegramConfig):
        self.config = config

    async def _send_image(
        self,
        bot: telegram.Bot,
        chat_id: int,
        file_path: Path,
        caption: str | None,
        use_html: bool,
    ) -> telegram.PhotoSize:
        async with aiofiles.open(file_path, "rb") as fd:
            input_file = telegram.InputFile(await fd.read())
            message = await _auto_retry(
                lambda: bot.send_photo(
                    chat_id=chat_id,
                    photo=input_file,
                    caption=caption,
                    disable_notification=True,
                    parse_mode=ParseMode.HTML if use_html else None,
                )
            )
            return max(message.photo, key=lambda p: p.file_size or 0)

    async def _send_video(
        self,
        bot: telegram.Bot,
        chat_id: int,
        file_path: Path,
        caption: str | None,
        use_html: bool,
    ) -> telegram.Video:
        async with aiofiles.open(file_path, "rb") as fd:
            input_file = telegram.InputFile(await fd.read())
            message = await _auto_retry(
                lambda: bot.send_video(
                    chat_id=chat_id,
                    video=input_file,
                    caption=caption,
                    disable_notification=True,
                    parse_mode=ParseMode.HTML if use_html else None,
                )
            )
            return cast(telegram.Video, message.video)

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
                video = await self._send_video(
                    bot,
                    chat_id,
                    file.path,
                    caption=None,
                    use_html=False,
                )
                items.append(telegram.InputMediaVideo(media=video))
            elif media_type == MediaType.PHOTO:
                photo = await self._send_image(
                    bot,
                    chat_id,
                    file.path,
                    caption=None,
                    use_html=False,
                )
                items.append(telegram.InputMediaPhoto(photo))
            else:
                raise ValueError(f"Unknown media type {media_type}")

        return items

    async def send_text_message(
        self,
        text: str,
        use_html: bool = False,
    ) -> None:
        async with telegram.Bot(token=self.config.token) as bot:
            await _auto_retry(
                lambda: bot.send_message(
                    chat_id=self.config.target_chat,
                    disable_notification=True,
                    disable_web_page_preview=True,
                    text=text,
                    parse_mode=ParseMode.HTML if use_html else None,
                )
            )

    async def send_documents_message(
        self,
        documents: list[MediaFile],
        *,
        caption: str | None,
        use_html: bool = False,
        disable_notification: bool = False,
    ) -> None:
        if not documents:
            raise ValueError("No input documents")

        chat_id = self.config.target_chat
        async with telegram.Bot(token=self.config.token) as bot:
            input_files = []
            is_multi_doc = len(documents) > 1
            for document in documents:
                async with aiofiles.open(document.path, "rb") as fd:
                    file_bytes = await fd.read()
                    _LOG.info(
                        "Document %s has %d bytes", document.path, len(file_bytes)
                    )
                    input_file = telegram.InputFile(
                        file_bytes,
                        filename=document.path.name,
                        attach=is_multi_doc,
                    )
                    input_files.append(input_file)

            if not is_multi_doc:
                await _auto_retry(
                    lambda: bot.send_document(
                        chat_id=chat_id,
                        document=input_file,
                        caption=caption,
                        disable_notification=disable_notification,
                        parse_mode=ParseMode.HTML if use_html else None,
                    )
                )
            else:
                media = []
                for index, input_file in enumerate(input_files):
                    if index == len(input_files) - 1:
                        doc_caption = caption
                    else:
                        doc_caption = None

                    doc = InputMediaDocument(
                        input_file,
                        caption=doc_caption,
                    )
                    media.append(doc)

                await _auto_retry(
                    lambda: bot.send_media_group(
                        chat_id=chat_id,
                        media=media,
                        disable_notification=disable_notification,
                        parse_mode=ParseMode.HTML if use_html else None,
                    )
                )

    async def send_image_message(
        self,
        image_files: list[MediaFile],
        caption: str | None,
        use_html: bool = False,
    ) -> None:
        chat_id = self.config.target_chat

        async with telegram.Bot(token=self.config.token) as bot:
            if len(image_files) == 1:
                await self._send_image(
                    bot,
                    chat_id,
                    image_files[0].path,
                    caption,
                    use_html,
                )
            else:
                items = await self._create_items(bot, image_files)
                if caption:
                    await _auto_retry(
                        lambda: bot.send_message(
                            chat_id,
                            caption,
                            disable_notification=True,
                            disable_web_page_preview=True,
                            parse_mode=ParseMode.HTML if use_html else None,
                        )
                    )
                await _auto_retry(
                    lambda: bot.send_media_group(
                        chat_id,
                        items,
                        disable_notification=True,
                    )
                )
