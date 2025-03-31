import abc

from twittergram.application.model.mail import Mail


class MailReader(abc.ABC):
    @abc.abstractmethod
    async def lookup_mailbox_id(self) -> str:
        pass

    @abc.abstractmethod
    async def list_mails(
        self,
        mailbox_id: str,
        mailbox_state: str | None,
    ) -> tuple[str, list[Mail]]:
        pass
