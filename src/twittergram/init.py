import logging
from pathlib import Path

import sentry_sdk
from injector import Injector, Module, provider

from twittergram.application import Application, repos, ports
from twittergram.config import load_env, Config, SentryConfig
from twittergram.infrastructure.adapters import (
    twitter_reader,
    twitter_downloader,
    telegram_uploader,
)
from twittergram.infrastructure.repos import state_repo

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


class ReposModule(Module):
    def __init__(self, config: Config):
        self.config = config

    @provider
    def provide_state_repo(self) -> repos.StateRepo:
        state_file = self.config.state.state_file

        if not state_file:
            raise ValueError("State file path not configured")

        return state_repo.FileStateRepo(Path(state_file))


class PortsModule(Module):
    def __init__(self, config: Config):
        self.config = config

    @provider
    def provide_telegram_uploader(self) -> ports.TelegramUploader:
        config = self.config.telegram
        if not config:
            raise ValueError("Missing Telegram config")

        return telegram_uploader.PtbTelegramUploader(config)

    @provider
    def provide_twitter_downloader(self) -> ports.TwitterDownloader:
        return twitter_downloader.TweepyTwitterDownloader(
            Path(self.config.download.download_directory),
        )

    @provider
    def provide_twitter_reader(self) -> ports.TwitterReader:
        config = self.config.twitter
        if not config:
            raise ValueError("Missing Twitter config")
        return twitter_reader.TweepyTwitterReader(config)


def initialize() -> Application:
    _setup_logging()

    config = Config.from_env(load_env(""))
    _setup_sentry(config.sentry)

    injector = Injector(
        modules=[
            ReposModule(config),
            PortsModule(config),
        ]
    )
    return injector.get(Application)
