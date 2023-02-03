import asyncio

from jmapc import Client, MailboxQueryFilterCondition, Error
from jmapc.methods import (
    MailboxQuery,
    MailboxQueryResponse,
    Response,
)

from twittergram.application.exceptions.io import IoException
from twittergram.application.ports import MailReader
from twittergram.config import MailConfig


class JmapcMailReader(MailReader):
    def __init__(self, config: MailConfig):
        self.config = config
        self._client = Client.create_with_api_token(
            host=config.api_host,
            api_token=config.token,
        )

    def _lookup_mailbox_id(self) -> str:
        client = self._client
        response: Response | Error = client.request(
            MailboxQuery(
                filter=MailboxQueryFilterCondition(name=self.config.mailbox_name),
            ),
        )

        if isinstance(response, Error):
            raise IoException(response.to_json())

        if not isinstance(response, MailboxQueryResponse):
            raise IoException(f"Invalid response type: {type(response)}")

        ids = response.ids
        if not isinstance(ids, list):
            raise IoException("Didn't get IDs as list")

        if len(ids) != 1:
            raise IoException("Could not find mailbox (got %d responses)", len(ids))

        return ids[0]

    async def lookup_mailbox_id(self) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._lookup_mailbox_id,
        )
