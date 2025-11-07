import logging
from dataclasses import dataclass

from injector import inject
from more_itertools import sliced

from twittergram.application import ports, repos
from twittergram.application.model import Mail, MailState

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardMails:
    reader: ports.MailReader
    state_repo: repos.StateRepo
    uploader: ports.TelegramUploader

    @staticmethod
    def _format_for_telegram(mail: Mail) -> str:
        result = ""

        if subject := mail.subject:
            result += subject
            result += "\n\n"

        result += mail.text_body

        return result

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

            for mail in reversed(mails):
                _LOG.info("Found mail with ID %s from %s", mail.id, mail.received_at)
                formatted = self._format_for_telegram(mail)
                for text_part in sliced(formatted, 4096):
                    await self.uploader.send_text_message(text=text_part)

                state.mailbox_state = mailbox_state
        finally:
            _LOG.debug("Storing state")
            await self.state_repo.store_state(state)
