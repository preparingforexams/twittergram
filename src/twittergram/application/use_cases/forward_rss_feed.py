import logging
from dataclasses import dataclass
from io import StringIO

from injector import inject

from twittergram.application import ports, repos
from twittergram.application.model import RssItem, RssState

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardRssFeed:
    reader: ports.RssReader
    sanitizer: ports.HtmlSanitizer
    state_repo: repos.StateRepo
    uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        _LOG.info("Not implemented")

        state = await self.state_repo.load_state(RssState)
        last_item_id = state.last_item_id
        last_item_time = state.last_item_time

        _LOG.info("Reading RSS items")
        items: list[RssItem] = []
        async for item in self.reader.list_items():
            if item.id == last_item_id:
                break

            if last_item_time is not None and item.published_at < last_item_time:
                _LOG.debug("Stopping collection because older item was encountered")
                break

            items.append(item)
            if not last_item_time and len(items) == 10:
                _LOG.debug("Stopping item collection due to missing stop ID")
                break

        if not items:
            _LOG.info("No items found")
            return

        # Reverse reverse chronological
        items.reverse()

        _LOG.info("Forwarding items")
        try:
            for item in items:
                with StringIO() as sanitized_text:
                    sanitized_text.write(await self.sanitizer.sanitize(item.title))
                    sanitized_text.write("\n\n")

                    if synopsis := item.synopsis:
                        sanitized_text.write(await self.sanitizer.sanitize(synopsis))
                        sanitized_text.write("\n")

                    if item.links:
                        sanitized_text.writelines([str(u) for u in item.links])

                    await self.uploader.send_text_message(
                        sanitized_text.getvalue(),
                        use_html=True,
                    )

                state.last_item_id = item.id
                state.last_item_time = item.published_at
        finally:
            _LOG.debug("Storing state")
            await self.state_repo.store_state(state)
