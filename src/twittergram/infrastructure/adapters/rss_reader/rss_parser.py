from collections.abc import AsyncIterable
from typing import cast

import httpx
from rss_parser import RSSParser
from rss_parser.models.rss import RSS
from rss_parser.models.rss.channel import Channel
from rss_parser.models.rss.item import Item as ParserRssItem
from rss_parser.models.types.date import validate_dt_or_str
from rss_parser.models.types.tag import Tag

from twittergram.application.exceptions.io import IoException
from twittergram.application.model import RssItem
from twittergram.application.ports import RssReader
from twittergram.config import RssConfig


class RssParserRssReader(RssReader):
    def __init__(self, config: RssConfig):
        self._feed_url = config.feed_url
        self._client = httpx.AsyncClient()

    async def list_items(self) -> AsyncIterable[RssItem]:
        try:
            response = await self._client.get(self._feed_url)
        except httpx.RequestError as e:
            raise IoException from e

        if not response.is_success:
            raise IoException(f"Got unsuccessful response {response.status_code}")

        feed = cast(RSS, RSSParser.parse(response.text, schema=RSS))
        channel = cast(Channel, feed.channel.content)
        for item_tag in cast(list[Tag[ParserRssItem]], channel.items):
            item = cast(ParserRssItem, item_tag.content)
            raw_pub_date = cast(str, cast(Tag[str], item.pub_date).content)
            pub_date = validate_dt_or_str(raw_pub_date)

            synopsis: str | None = None
            if synopsis_tag := item.synopsis:
                synopsis = cast(str, synopsis_tag.content)

            yield RssItem(
                id=cast(str, cast(Tag[str], item.guid).content),
                title=cast(str, item.title.content),
                synopsis=synopsis,
                published_at=pub_date,
                links=[link.content for link in item.links],
            )
