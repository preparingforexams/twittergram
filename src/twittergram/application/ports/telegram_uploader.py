import abc

from twittergram.domain.value_objects import MediaFile


class TelegramUploader(abc.ABC):
    @abc.abstractmethod
    async def send_text_message(
        self,
        text: str,
        use_html: bool = False,
    ) -> None:
        pass

    @abc.abstractmethod
    async def send_image_message(
        self,
        image_files: list[MediaFile],
        caption: str | None,
        use_html: bool = False,
    ) -> None:
        pass
