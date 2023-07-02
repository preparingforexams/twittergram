import logging
from dataclasses import dataclass

from injector import inject

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardXcode:
    async def __call__(self) -> None:
        _LOG.warning("Xcode forwarding not implemented yet")
