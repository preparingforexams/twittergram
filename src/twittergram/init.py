import logging

import sentry_sdk

from twittergram.application import Application
from twittergram.config import load_env, Config, SentryConfig
from twittergram.forward_tweets import ForwardTweets
from twittergram.twitter_reader import TwitterReader

_LOG = logging.getLogger(__name__)


def _setup_logging():
    logging.basicConfig()

    logging.root.level = logging.WARNING
    logging.getLogger(__package__).level = logging.DEBUG


def _setup_sentry(config: SentryConfig):
    dsn = config.dsn
    if not dsn:
        _LOG.warning("Sentry DSN not found")
        return

    sentry_sdk.init(
        dsn=dsn,
        release=config.release,
    )


def initialize() -> Application:
    _setup_logging()

    config = Config.from_env(load_env(""))
    _setup_sentry(config.sentry)

    return Application(
        forward_tweets=ForwardTweets(TwitterReader(config.twitter)),
    )
