import logging
from dataclasses import dataclass

import pendulum

from twittergram.twitter_reader import TwitterReader

_LOG = logging.getLogger(__name__)


@dataclass
class ForwardTweets:
    twitter_reader: TwitterReader

    async def __call__(self):
        # TODO: dynamic config
        username = "shirtsthtgohard"

        now = pendulum.now()

        _LOG.debug("Looking up user ID for user %s", username)
        user_id = await self.twitter_reader.lookup_user_id(username)

        # TODO: save and load until_id
        _LOG.info("Reading tweets for account %s", username)
        count = 0
        async for tweet in self.twitter_reader.list_tweets(user_id, now):
            _LOG.info("Found tweet with ID %d", tweet.id)
            count += 1
            if count == 10:
                break
