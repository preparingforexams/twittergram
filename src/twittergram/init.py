import logging
from pathlib import Path
from typing import Iterable

import sentry_sdk
from injector import Injector, Module, provider

from twittergram.application import Application, repos, ports
from twittergram.config import load_env, Config, SentryConfig
from twittergram.infrastructure.adapters import (
    twitter_reader,
    media_downloader,
    telegram_uploader,
    mastodon_reader,
    html_sanitizer,
    mail_reader,
    xcode_release_reader,
)
from twittergram.infrastructure.repos import state_repo

_LOG = logging.getLogger(__name__)


def _setup_logging() -> None:
    logging.basicConfig()

    logging.root.level = logging.WARNING
    logging.getLogger(__package__).level = logging.DEBUG


def _setup_sentry(config: SentryConfig) -> None:
    dsn = config.dsn
    if not dsn:
        _LOG.warning("Sentry DSN not found")
        return

    sentry_sdk.init(
        dsn=dsn,
        release=config.release,
    )


class ReposModule(Module):
    def __init__(self, config: Config) -> None:
        self.config = config

    @provider
    def provide_state_repo(self) -> repos.StateRepo:
        state_file = self.config.state.state_file

        if not state_file:
            raise ValueError("State file path not configured")

        return state_repo.FileStateRepo(Path(state_file))


class PortsModule(Module):
    def __init__(self, config: Config) -> None:
        self.config = config

    @provider
    def provide_mail_reader(self) -> ports.MailReader:
        config = self.config.mail

        if not config:
            raise ValueError("Missing mail config")

        return mail_reader.JmapcMailReader(config)

    @provider
    def provide_html_sanitizer(self) -> ports.HtmlSanitizer:
        config = self.config.sanitizer

        match config.type:
            case "naive":
                return html_sanitizer.NaiveHtmlSanitizer()
            case other:
                raise ValueError(f"Unsupported HTML sanitizer type: {other}")

    @provider
    def provide_mastodon_reader(self) -> ports.MastodonReader:
        config = self.config.mastodon
        if not config:
            raise ValueError("Missing mastodon config")

        return mastodon_reader.MastodonPyMastodonReader(config)

    @provider
    def provide_telegram_uploader(self) -> ports.TelegramUploader:
        config = self.config.telegram
        if not config:
            raise ValueError("Missing Telegram config")

        return telegram_uploader.PtbTelegramUploader(config)

    @provider
    def provide_twitter_downloader(self) -> ports.MediaDownloader:
        download_directory = self.config.download.download_directory

        if not download_directory:
            raise ValueError("Missing download directory")

        return media_downloader.HttpMediaDownloader(
            Path(download_directory),
        )

    @provider
    def provide_twitter_reader(self) -> ports.TwitterReader:
        config = self.config.twitter
        if not config:
            raise ValueError("Missing Twitter config")
        return twitter_reader.TweepyTwitterReader(config)

    @provider
    def provide_xcode_release_reader(self) -> ports.XcodeReleaseReader:
        return xcode_release_reader.XcrXcodeReleaseReader()


def initialize(env_names: Iterable[str]) -> Application:
    _setup_logging()

    config = Config.from_env(load_env(env_names))
    _setup_sentry(config.sentry)

    injector = Injector(
        modules=[
            ReposModule(config),
            PortsModule(config),
        ]
    )
    return Application(injector)
