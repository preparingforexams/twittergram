import asyncio
import logging
from dataclasses import dataclass

import pendulum
from injector import inject

from twittergram.application import ports, repos
from twittergram.domain.model import State, Tweet

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardTweets:
    state_repo: repos.StateRepo
    telegram_uploader: ports.TelegramUploader
    twitter_downloader: ports.TwitterDownloader
    twitter_reader: ports.TwitterReader

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

        _LOG.info("Found %d new tweets, downloading media now", len(tweets))
        downloads = [self.twitter_downloader.download(tweet) for tweet in tweets]
        _LOG.debug("Waiting up to 10 minutes until downloads are done")
        done, pending = await asyncio.wait(downloads, timeout=600)

        if pending:
            _LOG.warning("%d downloads did not finish in time", len(pending))

        media_files = []
        for task in done:
            media_files.extend(task.result())
        media_files.reverse()

        _LOG.info("Downloaded %d media files, uploading to Telegram", len(media_files))
        await self.telegram_uploader.upload_media(media_files)

        _LOG.debug("Storing latest tweet ID")
        state.last_tweet_id = tweets[0].id
        await self.state_repo.store_state(state)
