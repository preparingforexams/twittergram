import logging
from dataclasses import dataclass

from injector import inject

from twittergram.application import ports, repos

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardMails:
    reader: ports.MailReader
    state_repo: repos.StateRepo
    uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        _LOG.info("Looking up mailbox ID")
        mailbox_id = await self.reader.lookup_mailbox_id()
        _LOG.info("Found ID %s", mailbox_id)
        # TODO: introduce new state type
        # TODO: forward mails
