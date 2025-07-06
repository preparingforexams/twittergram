import abc
from pathlib import Path


class GalleryDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, directory:Path, url: str) -> list[Path]:
        pass
