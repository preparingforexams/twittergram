import logging
from dataclasses import dataclass
from typing import Self

from bs_config import Env

_LOG = logging.getLogger(__name__)


@dataclass
class SentryConfig:
    dsn: str | None
    release: str

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            dsn=env.get_string("SENTRY_DSN"),
            release=env.get_string("APP_VERSION", default="debug"),
        )


@dataclass
class BlueskyConfig:
    user: str
    password: str
    author_id: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        scoped = env.scoped("BLUESKY_")

        try:
            user = scoped.get_string("USER", required=True)
            password = scoped.get_string("PASSWORD", required=True)
            author_id = scoped.get_string("AUTHOR_ID", required=True)
        except ValueError as e:
            _LOG.debug("Bluesky config not complete: %s", e)
            return None

        return cls(
            user=user,
            password=password,
            author_id=author_id,
        )


@dataclass
class DownloadConfig:
    download_directory: str | None

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            download_directory=env.get_string("DOWNLOAD_DIR"),
        )


@dataclass
class MailConfig:
    api_host: str
    mailbox_name: str
    token: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        env = env.scoped("MAIL_")
        mailbox_name = env.get_string("MAILBOX_NAME")
        token = env.get_string("TOKEN")

        if not (mailbox_name and token):
            return None

        return cls(
            api_host=env.get_string(
                "API_HOST",
                default="api.fastmail.com",
            ),
            mailbox_name=mailbox_name,
            token=token,
        )


@dataclass
class HtmlSanitizerConfig:
    type: str

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            type=env.get_string("HTML_SANITIZER_TYPE", default="naive"),
        )


@dataclass
class MastodonConfig:
    api_base_url: str
    client_id: str
    client_secret: str
    source_account: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        env = env.scoped("MASTODON_")
        client_id = env.get_string("CLIENT_ID")
        client_secret = env.get_string("CLIENT_SECRET")
        source_account = env.get_string("SOURCE_ACCOUNT")
        if not (client_id and client_secret and source_account):
            return None

        return cls(
            api_base_url=env.get_string(
                "API_BASE_URL",
                default="https://mastodon.social",
            ),
            client_id=client_id,
            client_secret=client_secret,
            source_account=source_account,
        )


@dataclass
class RedditConfig:
    client_id: str
    client_secret: str
    user_agent: str
    source_username: str
    subreddit_filter: str | None

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        env = env.scoped("REDDIT_")
        client_id = env.get_string("CLIENT_ID")
        client_secret = env.get_string("CLIENT_SECRET")

        if not (client_id and client_secret):
            return None

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=env.get_string("USER_AGENT", default="twittergram"),
            source_username=env.get_string("SOURCE_USERNAME", required=True),
            subreddit_filter=env.get_string("SUBREDDIT_FILTER"),
        )


@dataclass
class ConfigMapStateConfig:
    namespace: str
    name_prefix: str
    name_suffix: str | None

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        env = env.scoped("STATE_CONFIG_MAP_")
        try:
            return cls(
                namespace=env.get_string("NAMESPACE", required=True),
                name_prefix=env.get_string("NAME_PREFIX", required=True),
                name_suffix=env.get_string("NAME_SUFFIX"),
            )
        except ValueError:
            return None


@dataclass
class StateConfig:
    type: str
    config_map: ConfigMapStateConfig | None
    state_file: str | None

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            type=env.get_string("STATE_TYPE", default="file"),
            config_map=ConfigMapStateConfig.from_env(env),
            state_file=env.get_string("STATE_FILE_PATH"),
        )


@dataclass
class TelegramConfig:
    target_chat: int
    token: str
    upload_chat: int

    @classmethod
    def from_env(cls, env: Env) -> Self:
        env = env.scoped("TELEGRAM_")
        return cls(
            target_chat=env.get_int("TARGET_CHAT_ID", required=True),
            token=env.get_string("TOKEN", required=True),
            upload_chat=env.get_int("UPLOAD_CHAT_ID", required=True),
        )


@dataclass
class TwitterConfig:
    source_account: str
    token: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        env = env.scoped("TWITTER_")
        source_account = env.get_string("SOURCE_ACCOUNT")
        token = env.get_string("TOKEN")

        if not (source_account and token):
            return None

        return cls(
            source_account=source_account,
            token=token,
        )


@dataclass
class Config:
    bluesky: BlueskyConfig | None
    download: DownloadConfig
    mail: MailConfig | None
    mastodon: MastodonConfig | None
    reddit: RedditConfig | None
    sanitizer: HtmlSanitizerConfig
    sentry: SentryConfig
    state: StateConfig
    telegram: TelegramConfig
    twitter: TwitterConfig | None

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            bluesky=BlueskyConfig.from_env(env),
            download=DownloadConfig.from_env(env),
            mail=MailConfig.from_env(env),
            mastodon=MastodonConfig.from_env(env),
            reddit=RedditConfig.from_env(env),
            sanitizer=HtmlSanitizerConfig.from_env(env),
            sentry=SentryConfig.from_env(env),
            state=StateConfig.from_env(env),
            telegram=TelegramConfig.from_env(env),
            twitter=TwitterConfig.from_env(env),
        )
