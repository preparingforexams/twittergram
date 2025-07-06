import logging
from collections.abc import Iterable
from pathlib import Path

import sentry_sdk
from bs_config import Env
from bs_state import StateStorage
from injector import Injector, Module, multiprovider, provider

from twittergram.application import Application, ports, repos
from twittergram.application.model import State
from twittergram.config import (
    Config,
    ConfigMapStateConfig,
    RedditConfig,
    SentryConfig,
)
from twittergram.infrastructure.adapters import (
    bluesky_reader,
    html_sanitizer,
    mail_reader,
    mastodon_reader,
    media_downloader,
    reddit_reader,
    rss_reader,
    telegram_uploader,
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


class ConfigsModule(Module):
    def __init__(self, config: Config) -> None:
        self.config = config

    @provider
    def provide_reddit_config(self) -> RedditConfig:
        config = self.config.reddit
        if config is None:
            raise ValueError("Missing Reddit config")
        return config


class ReposModule(Module):
    def __init__(self, config: Config) -> None:
        self.config = config

    @staticmethod
    def _create_file_repo(file_path: str) -> repos.StateRepo:
        from bs_state.implementation import file_storage

        async def load_file_storage(
            initial_state: State,
        ) -> StateStorage[State]:
            return await file_storage.load(
                initial_state=initial_state,
                file=Path(file_path),
            )

        return state_repo.BsStateRepo(load_file_storage)

    @staticmethod
    def _camel_to_slug(value: str) -> str:
        result = value[0].lower()
        for char in value[1:]:
            if char.isupper():
                result += f"-{char.lower()}"
            else:
                result += char
        return result

    def _create_config_map_repo(self, config: ConfigMapStateConfig) -> repos.StateRepo:
        from bs_state.implementation import config_map_storage

        async def load_configmap_storage(
            initial_state: State,
        ) -> StateStorage[State]:
            slug_name = self._camel_to_slug(type(initial_state).__name__)
            config_map_name = f"{config.name_prefix}-{slug_name}"
            if config.name_suffix is not None:
                config_map_name = f"{config_map_name}-{config.name_suffix}"

            return await config_map_storage.load(
                initial_state=initial_state,
                namespace=config.namespace,
                config_map_name=config_map_name,
            )

        return state_repo.BsStateRepo(load_configmap_storage)

    @provider
    def provide_state_repo(self) -> repos.StateRepo:
        state_type = self.config.state.type

        match state_type:
            case "file":
                state_file = self.config.state.state_file
                if not state_file:
                    raise ValueError("State file path not configured")
                return self._create_file_repo(state_file)
            case "configmap":
                config_map_config = self.config.state.config_map
                if not config_map_config:
                    raise ValueError("ConfigMap state is not configured, but selected")
                return self._create_config_map_repo(config_map_config)
            case _:
                raise ValueError(f"Unknown state repo type: {state_type}")


class PortsModule(Module):
    def __init__(self, config: Config) -> None:
        self.config = config

    @provider
    def provide_bluesky_reader(self) -> ports.BlueskyReader:
        config = self.config.bluesky

        if not config:
            raise ValueError("Missing Bluesky config")

        return bluesky_reader.AtprotoBlueskyReader(config)

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
    def provide_reddit_reader(self, config: RedditConfig) -> ports.RedditReader:
        return reddit_reader.PrawRedditReader(config)

    @provider
    def provide_rss_reader(self) -> ports.RssReader:
        if rss_config := self.config.rss:
            return rss_reader.RssParserRssReader(rss_config)

        raise ValueError("RSS config is missing")

    @provider
    def provide_telegram_uploader(self) -> ports.TelegramUploader:
        return telegram_uploader.PtbTelegramUploader(self.config.telegram)

    @multiprovider
    def provide_media_downloader(self) -> list[ports.MediaDownloader]:
        download_directory = self.config.download.download_directory

        if not download_directory:
            raise ValueError("Missing download directory")

        return [
            media_downloader.GalleryDlMediaDownloader(
                Path(download_directory),
            ),
            media_downloader.HttpMediaDownloader(
                Path(download_directory),
            ),
        ]

    @provider
    def provide_xcode_release_reader(self) -> ports.XcodeReleaseReader:
        return xcode_release_reader.XcrXcodeReleaseReader()


def initialize(env_names: Iterable[str]) -> Application:
    _setup_logging()

    config = Config.from_env(
        Env.load(
            include_default_dotenv=True,
            additional_dotenvs=list(env_names),
        )
    )
    _setup_sentry(config.sentry)

    injector = Injector(
        modules=[
            ConfigsModule(config),
            ReposModule(config),
            PortsModule(config),
        ]
    )
    return Application(injector)
