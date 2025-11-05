from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True)
class Mail:
    id: str
    thread_id: str
    received_at: datetime
    subject: str | None
    text_body: str
