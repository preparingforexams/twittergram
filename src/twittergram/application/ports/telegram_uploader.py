import abc

from twittergram.application.model import MediaFile


class TelegramUploader(abc.ABC):
    @abc.abstractmethod
    async def send_text_message(
        self,
        text: str,
        use_html: bool = False,
    ) -> None:
        pass

    @abc.abstractmethod
    async def send_documents_message(
        self,
        documents: list[MediaFile],
        *,
        caption: str | None,
        use_html: bool = False,
        file_name: str | None = None,
        disable_notification: bool = False,
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
