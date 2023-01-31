import logging
from dataclasses import dataclass

import pendulum
from injector import inject

from twittergram.application import ports, repos
from twittergram.application.exceptions.media import UnsupportedMediaTypeException
from twittergram.domain.model import State, Tweet
from twittergram.domain.value_objects import MediaFile

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class ForwardTweets:
    state_repo: repos.StateRepo
    telegram_uploader: ports.TelegramUploader
    twitter_downloader: ports.TwitterDownloader
    twitter_reader: ports.TwitterReader

    @staticmethod
    def _is_idiotic(text: str) -> bool:
        return "@elhotzo" in text and (" folgt " in text or " entfolgt," in text)

    async def __call__(self) -> None:
        now = pendulum.now()

        _LOG.debug("Looking up user ID for twitter source account")
        user_id = await self.twitter_reader.lookup_user_id()

        state = await self.state_repo.load_state() or State.initial()
        until_id = state.last_tweet_id

        _LOG.info("Reading tweets for account %s", user_id)
        tweets: list[Tweet] = []
        async for tweet in self.twitter_reader.list_tweets(
            user_id,
            start_time=now,
            until_id=until_id,
        ):
            tweets.append(tweet)
            if not until_id and len(tweets) == 100:
                _LOG.debug("Stopping tweet collection due to missing until_id")
                break

        if not tweets:
            _LOG.info("No tweets found")
            return

        # Reverse reverse chronological
        tweets.reverse()

        media_by_tweet_id: dict[int, list[MediaFile] | None] = {}

        _LOG.info("Found %d new tweets, downloading media now", len(tweets))

        for tweet in tweets:
            media = tweet.attachments.media
            if media:
                try:
                    files = await self.twitter_downloader.download(media)
                except UnsupportedMediaTypeException as e:
                    _LOG.warning("Could not download medium", exc_info=e)
                    media_by_tweet_id[tweet.id] = None
                else:
                    media_by_tweet_id[tweet.id] = files
            else:
                media_by_tweet_id[tweet.id] = []

        try:
            for tweet in tweets:
                if tweet.attachments.media:
                    media_files = media_by_tweet_id[tweet.id]

                    if media_files:
                        await self.telegram_uploader.send_image_message(
                            media_files,
                            tweet.text,
                        )
                    else:
                        _LOG.info("Dropping tweet %d with None media files", tweet.id)
                elif tweet.text and not self._is_idiotic(tweet.text):
                    await self.telegram_uploader.send_text_message(tweet.text)
                else:
                    _LOG.info("Got tweet without media or text")

                state.last_tweet_id = tweet.id
        finally:
            _LOG.debug("Storing state")
            await self.state_repo.store_state(state)
