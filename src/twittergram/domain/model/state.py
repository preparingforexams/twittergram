from __future__ import annotations

from dataclasses import dataclass


@dataclass
class State:
    last_toot_id: int | None = None
    last_tweet_id: int | None = None

    @classmethod
    def initial(cls) -> State:
        return cls(
            last_toot_id=None,
            last_tweet_id=None,
        )
