import asyncio
import logging
from datetime import datetime
from typing import cast

from jmapc import (
    Client,
    Comparator,
    Email,
    EmailQueryFilterCondition,
    Error,
    MailboxQueryFilterCondition,
    Ref,
)
from jmapc.methods import (
    EmailGet,
    EmailGetResponse,
    EmailQuery,
    EmailQueryChanges,
    EmailQueryChangesResponse,
    EmailQueryResponse,
    MailboxQuery,
    MailboxQueryResponse,
    Response,
)

from twittergram.application.exceptions.io import IoException
from twittergram.application.ports import MailReader
from twittergram.config import MailConfig
from twittergram.domain.model import Mail

_LOG = logging.getLogger(__name__)


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

    @staticmethod
    def _parse_mail(mail: Email) -> Mail:
        text_body = mail.text_body or []
        body_values = mail.body_values or {}
        part_ids = [cast(str, tb.part_id) for tb in text_body]
        return Mail(
            id=cast(str, mail.id),
            thread_id=cast(str, mail.thread_id),
            received_at=cast(datetime, mail.received_at),
            subject=mail.subject,
            text_body="\n\n".join(
                cast(str, body_values[part_id].value) for part_id in part_ids
            ),
        )

    def _list_mails(
        self,
        mailbox_id: str,
        mailbox_state: str | None,
    ) -> tuple[str, list[Mail]]:
        client = self._client

        if mailbox_state is None:
            _LOG.info("Making initial query")
            methods = [
                EmailQuery(
                    sort=[Comparator("receivedAt", is_ascending=False)],
                    limit=10,
                    filter=EmailQueryFilterCondition(
                        in_mailbox=mailbox_id,
                    ),
                ),
                EmailGet(
                    ids=Ref("/ids"),
                    fetch_text_body_values=True,
                ),
            ]
            result = client.request(methods)
        else:
            _LOG.info("Looking for changes with existing state")
            methods = [
                EmailQueryChanges(
                    since_query_state=mailbox_state,
                    sort=[Comparator("receivedAt", is_ascending=False)],
                    filter=EmailQueryFilterCondition(
                        in_mailbox=mailbox_id,
                    ),
                ),
                EmailGet(
                    ids=Ref("/added/*/id"),
                    fetch_text_body_values=True,
                ),
            ]
            result = client.request(methods)

        query_result, email_result = result

        if isinstance(query_result, Error):
            raise IoException(f"Could not query mails: {query_result.to_json()}")

        if isinstance(email_result, Error):
            raise IoException(f"Could not get mails: {email_result.to_json()}")

        query_response = cast(
            EmailQueryResponse | EmailQueryChangesResponse,
            query_result.response,
        )
        new_state: str
        if isinstance(query_response, EmailQueryResponse):
            new_state = query_response.query_state
        else:
            new_state = query_response.new_query_state

        email_data = cast(EmailGetResponse, email_result.response).data
        mails = [self._parse_mail(m) for m in email_data]

        return new_state, mails

    async def list_mails(
        self,
        mailbox_id: str,
        mailbox_state: str | None,
    ) -> tuple[str, list[Mail]]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._list_mails(
                mailbox_id=mailbox_id,
                mailbox_state=mailbox_state,
            ),
        )
