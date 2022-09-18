import logging
from dataclasses import dataclass

import pendulum

from twittergram.state_repo import StateRepo, State
from twittergram.twitter_reader import TwitterReader, Tweet

_LOG = logging.getLogger(__name__)


@dataclass
class ForwardTweets:
    state_repo: StateRepo
    twitter_reader: TwitterReader

    async def __call__(self):
        # TODO: dynamic config
        username = "shirtsthtgohard"

        now = pendulum.now()

        _LOG.debug("Looking up user ID for user %s", username)
        user_id = await self.twitter_reader.lookup_user_id(username)

        state = await self.state_repo.load_state() or State.initial()
        until_id = state.last_tweet_id

        _LOG.info("Reading tweets for account %s", username)
        tweets: list[Tweet] = []
        async for tweet in self.twitter_reader.list_tweets(
            user_id,
            start_time=now,
            until_id=until_id,
        ):
            tweets.append(tweet)
            if not until_id and len(tweets) == 10:
                _LOG.debug("Stopping tweet collection due to missing until_id")
                break

        if not tweets:
            _LOG.info("No tweets found")
            return

        _LOG.info("Found %d new tweets", len(tweets))
        # TODO: do stuff with it

        _LOG.debug("Storing latest tweet ID")
        state.last_tweet_id = tweets[0].id
        await self.state_repo.store_state(state)
