import logging
from dataclasses import dataclass

from injector import inject

from twittergram.application import ports, repos
from twittergram.domain.model import MailState

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardMails:
    reader: ports.MailReader
    state_repo: repos.StateRepo
    uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        _LOG.debug("Loading state")
        state = await self.state_repo.load_state(MailState)

        mailbox_id = state.mailbox_id

        if not mailbox_id:
            _LOG.info("Looking up mailbox ID")
            mailbox_id = await self.reader.lookup_mailbox_id()
            _LOG.info("Found ID %s", mailbox_id)
            state.mailbox_id = mailbox_id

        _LOG.info("Querying mails")
        try:
            mailbox_state, mails = await self.reader.list_mails(
                mailbox_id,
                state.mailbox_state,
            )
            for mail in mails:
                _LOG.info("Found mail with ID %s. Subject: %s", mail.id, mail.subject)

            # state.mailbox_state = mailbox_state
        finally:
            await self.state_repo.store_state(state)
