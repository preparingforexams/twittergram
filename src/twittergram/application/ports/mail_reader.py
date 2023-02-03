import abc


class MailReader(abc.ABC):
    @abc.abstractmethod
    async def lookup_mailbox_id(self) -> str:
        pass
