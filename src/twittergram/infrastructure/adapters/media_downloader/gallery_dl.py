import logging
from pathlib import Path

import gallery_dl
from httpx import URL

from twittergram.application.model import Medium, MediaType, MediaFile
from twittergram.application.ports import MediaDownloader
from multiprocessing import
_LOG = logging.getLogger(__name__)


class GalleryDlMediaDownloader(MediaDownloader):
    def __init__(self, directory: Path):
        self.directory = directory

    async def is_supported(self, medium: Medium) -> bool:
        if not medium.type == MediaType.PHOTO:
            return False

        url = URL(medium.url)
        if url.host == "www.reddit.com" and url.path.startswith("/gallery/"):
            return True

        return False

    async def download(self, media: list[Medium]) -> list[MediaFile]:

        downloader = gallery_dl.main()
