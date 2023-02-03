import logging
from dataclasses import dataclass

from injector import inject

from twittergram.application import ports, repos
from twittergram.application.exceptions.media import UnsupportedMediaTypeException
from twittergram.domain.model import State, Toot
from twittergram.domain.value_objects import MediaFile

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardToots:
    state_repo: repos.StateRepo
    reader: ports.MastodonReader
    downloader: ports.MediaDownloader
    uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        _LOG.debug("Looking up user ID for Mastodon source account")
        user_id = await self.reader.lookup_user_id()

        state = await self.state_repo.load_state() or State.initial()
        until_id = state.last_toot_id

        _LOG.info("Reading toots for account %s", user_id)
        toots: list[Toot] = []
        async for toot in self.reader.list_toots(
            user_id,
            until_id=until_id,
        ):
            toots.append(toot)
            if not until_id and len(toots) == 10:
                _LOG.debug("Stopping toot collection due to missing until_id")
                break

        if not toots:
            _LOG.info("No toots found")
            return

        # TODO: check order
        # Reverse reverse chronological
        toots.reverse()

        media_by_toot_id: dict[int, list[MediaFile] | None] = {}

        _LOG.info("Found %d new toots, downloading media now", len(toots))

        for toot in toots:
            media = toot.media_attachments
            if media:
                try:
                    files = await self.downloader.download(media)
                except UnsupportedMediaTypeException as e:
                    _LOG.warning("Could not download medium", exc_info=e)
                    media_by_toot_id[toot.id] = None
                else:
                    media_by_toot_id[toot.id] = files
            else:
                media_by_toot_id[toot.id] = []

        _LOG.info("Forwarding toots")
        try:
            for toot in toots:
                if toot.media_attachments:
                    media_files = media_by_toot_id[toot.id]

                    if media_files:
                        await self.uploader.send_image_message(
                            media_files,
                            toot.content,
                            use_html=True,
                        )
                    else:
                        _LOG.info("Dropping toot %d with None media files", toot.id)
                elif toot.content:
                    await self.uploader.send_text_message(toot.content)
                else:
                    _LOG.info("Got toot without media or text")

                state.last_toot_id = toot.id
        finally:
            _LOG.debug("Storing state")
            await self.state_repo.store_state(state)
