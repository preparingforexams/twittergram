from datetime import date
from typing import Any, AsyncIterable, cast

from httpx import AsyncClient, RequestError

from twittergram.application.exceptions.io import IoException
from twittergram.application.ports import XcodeReleaseReader
from twittergram.domain.model import URL, XcodeRelease


class XcrXcodeReleaseReader(XcodeReleaseReader):
    def __init__(self) -> None:
        self._client = AsyncClient(timeout=10)

    async def get_releases(self) -> AsyncIterable[XcodeRelease]:
        try:
            response = await self._client.get(
                "https://xcodereleases.com/data.json",
                headers=dict(Accept="application/json"),
            )
        except RequestError as e:
            raise IoException from e

        if 500 <= response.status_code < 600:
            raise IoException(f"Encountered server error {response.status_code}")

        raw_releases = cast(list[dict[str, Any]], response.json())

        for raw_release in raw_releases:
            release = self._build_release(raw_release)
            if release:
                yield release

    @staticmethod
    def _build_release(raw: dict[str, Any]) -> XcodeRelease | None:
        version = raw["version"]
        if not version["release"].get("release"):
            # For releases:
            #
            # "version": {
            #     "number": "14.3.1",
            #     "build": "14E300c",
            #     "release": {
            #       "release": true
            #     }
            #   },

            # For betas:
            #
            # "version": {
            #     "number": "15.0",
            #     "build": "15A5161b",
            #     "release": {
            #       "beta": 2
            #     }
            #   },
            return None

        release_date = date(**raw["date"])
        release_notes_url = URL(raw["links"]["notes"]["url"])
        return XcodeRelease(
            version_number=version["number"],
            version_build=version["build"],
            release_date=release_date,
            release_notes=release_notes_url,
        )
