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
            dsn=env.get_string("sentry-dsn"),
            release=env.get_string("app-version", default="debug"),
        )


@dataclass
class BlueskyConfig:
    user: str
    password: str
    author_id: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        try:
            user = env.get_string("username", required=True)
            password = env.get_string("password", required=True)
            author_id = env.get_string("author-id", required=True)
        except ValueError:
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
            download_directory=env.get_string("download-dir"),
        )


@dataclass
class MailConfig:
    api_host: str
    mailbox_name: str
    token: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        mailbox_name = env.get_string("mailbox-name")
        token = env.get_string("token")

        if not (mailbox_name and token):
            return None

        return cls(
            api_host=env.get_string(
                "api-host",
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
            type=env.get_string(
                "html-sanitizer-type",
                default="naive",
            ),
        )


@dataclass
class MastodonConfig:
    api_base_url: str
    client_id: str
    client_secret: str
    source_account: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        client_id = env.get_string("client-id")
        client_secret = env.get_string("client-secret")
        source_account = env.get_string("source-account")
        if not (client_id and client_secret and source_account):
            return None

        return cls(
            api_base_url=env.get_string(
                "api-base-url",
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
        client_id = env.get_string("client-id")
        client_secret = env.get_string("client-secret")

        if not (client_id and client_secret):
            return None

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=env.get_string("user-agent", default="twittergram"),
            source_username=env.get_string("source-username", required=True),
            subreddit_filter=env.get_string("subreddit-filter"),
        )


@dataclass(frozen=True, kw_only=True)
class RssConfig:
    order: str | None
    feed_url: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        try:
            return cls(
                feed_url=env.get_string("feed-url", required=True),
                order=env.get_string("order"),
            )
        except ValueError:
            return None


@dataclass
class ConfigMapStateConfig:
    namespace: str
    name_prefix: str
    name_suffix: str | None

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        try:
            return cls(
                namespace=env.get_string("namespace", required=True),
                name_prefix=env.get_string("name-prefix", required=True),
                name_suffix=env.get_string("name-suffix"),
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
            type=env.get_string("type", default="file"),
            config_map=ConfigMapStateConfig.from_env(env / "config-map"),
            state_file=env.get_string("file-path"),
        )


@dataclass
class TelegramConfig:
    target_chat: int
    token: str
    upload_chat: int

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            target_chat=env.get_int("target-chat-id", required=True),
            token=env.get_string("token", required=True),
            upload_chat=env.get_int("upload-chat-id", required=True),
        )


@dataclass
class Config:
    bluesky: BlueskyConfig | None
    download: DownloadConfig
    mail: MailConfig | None
    mastodon: MastodonConfig | None
    reddit: RedditConfig | None
    rss: RssConfig | None
    sanitizer: HtmlSanitizerConfig
    sentry: SentryConfig
    state: StateConfig
    telegram: TelegramConfig

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            bluesky=BlueskyConfig.from_env(env / "bluesky"),
            download=DownloadConfig.from_env(env),
            mail=MailConfig.from_env(env / "mail"),
            mastodon=MastodonConfig.from_env(env / "mastodon"),
            reddit=RedditConfig.from_env(env / "reddit"),
            rss=RssConfig.from_env(env / "rss"),
            sanitizer=HtmlSanitizerConfig.from_env(env),
            sentry=SentryConfig.from_env(env),
            state=StateConfig.from_env(env / "state"),
            telegram=TelegramConfig.from_env(env / "telegram"),
        )
