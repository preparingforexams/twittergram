from __future__ import annotations

from dataclasses import dataclass


@dataclass
class State:
    last_tweet_id: int | None

    @classmethod
    def initial(cls) -> State:
        return cls(
            last_tweet_id=None,
        )
