from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Mail:
    id: str
    thread_id: str
    received_at: datetime
    subject: str | None
    text_body: str
