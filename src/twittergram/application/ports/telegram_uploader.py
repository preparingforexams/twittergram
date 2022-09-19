import abc
from pathlib import Path


class TelegramUploader(abc.ABC):
    @abc.abstractmethod
    async def upload_media(self, media_files: list[Path]):
        pass
