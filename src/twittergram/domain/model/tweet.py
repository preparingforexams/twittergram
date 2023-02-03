from dataclasses import dataclass

from twittergram.domain.model.media import Medium


@dataclass(frozen=True)
class TweetAttachments:
    media: list[Medium]


@dataclass(frozen=True)
class Tweet:
    id: int
    text: str | None
    attachments: TweetAttachments
