import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from io import StringIO

from injector import inject

from twittergram.application import ports, repos
from twittergram.application.model import RssItem, RssState
from twittergram.config import RssConfig

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardRssFeed:
    config: RssConfig
    reader: ports.RssReader
    sanitizer: ports.HtmlSanitizer
    state_repo: repos.StateRepo
    uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        state = await self.state_repo.load_state(RssState)
        last_item_id = state.last_item_id
        last_item_time = state.last_item_time

        _LOG.info("Reading RSS items")
        items: list[RssItem] = []
        async for item in self.reader.list_items():
            items.append(item)

        match self.config.order:
            case "chronological":
                # Nothing to do
                pass
            case "reverse_chronological":
                # Reverse reverse chronological
                items.reverse()
            case None:
                items.sort(key=lambda i: i.published_at)
            case other:
                raise ValueError(f"Unknown order type: {other}")

        items = self._filter_items(
            items,
            last_item_id=last_item_id,
            last_item_time=last_item_time,
        )

        if not items:
            _LOG.info("No items found")
            return

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

    @staticmethod
    def _filter_items(
        items: Sequence[RssItem],
        *,
        last_item_id: str | None,
        last_item_time: datetime | None,
    ) -> list[RssItem]:
        result = []

        for item in reversed(items):
            if item.id == last_item_id:
                break

            if last_item_time is not None and item.published_at < last_item_time:
                _LOG.info("Stopping collection because older item was encountered")
                break

            result.append(item)
            if not last_item_time and len(result) == 10:
                _LOG.info("Stopping item collection due to missing stop ID")
                break

        return result
