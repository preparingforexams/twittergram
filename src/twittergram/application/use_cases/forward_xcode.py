import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from injector import inject

from twittergram.application.model import XcodeState

if TYPE_CHECKING:
    from twittergram.application import model, ports, repos

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardXcode:
    state_repo: repos.StateRepo
    telegram_uploader: ports.TelegramUploader
    xcode_release_reader: ports.XcodeReleaseReader

    async def __call__(self) -> None:
        state = await self.state_repo.load_state(XcodeState)

        releases = self.xcode_release_reader.get_releases()
        releases_to_forward: list[model.XcodeRelease]

        last_release_build = state.last_release_build
        if not last_release_build:
            _LOG.warning("Running for the first time. Will use the first release.")
            releases_to_forward = [await anext(releases)]  # type: ignore[call-overload]
        else:
            releases_to_forward = []
            async for release in releases:
                if release.version_build == last_release_build:
                    break

                releases_to_forward.append(release)

        if not releases_to_forward:
            _LOG.info("Found no new releases")
            return

        # We want to receive them in order of release date
        releases_to_forward.reverse()

        _LOG.info("Found %d new releases", len(releases_to_forward))

        try:
            for release in releases_to_forward:
                message = self._build_message(release)
                await self.telegram_uploader.send_text_message(
                    message,
                    use_html=True,
                )
                state.last_release_build = release.version_build
        finally:
            _LOG.info("Storing updated state")
            await self.state_repo.store_state(state)

    @staticmethod
    def _build_message(release: model.XcodeRelease) -> str:
        return (
            f"Xcode {release.version_number} was released on {release.release_date}."
            f' <a href="{release.release_notes}">Click here for the release notes</a>.'
        )
