import asyncio
import logging
from dataclasses import dataclass

_LOG = logging.getLogger(__name__)


@dataclass
class ForwardTweets:
    async def __call__(self):
        _LOG.info("Stub forward tweets use case")
        await asyncio.sleep(10)
