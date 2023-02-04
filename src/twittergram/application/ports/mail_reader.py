import abc
from typing import Iterable

from twittergram.domain.model.mail import Mail


class MailReader(abc.ABC):
    @abc.abstractmethod
    async def lookup_mailbox_id(self) -> str:
        pass

    @abc.abstractmethod
    async def list_mails(
        self,
        mailbox_id: str,
        mailbox_state: str | None,
    ) -> tuple[str, Iterable[Mail]]:
        pass
