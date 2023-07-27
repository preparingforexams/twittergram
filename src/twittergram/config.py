from dataclasses import dataclass
from typing import Iterable, Self, cast, overload

from dotenv import dotenv_values


class Env:
    def __init__(self, values: dict[str, str]):
        self._values = values

    @overload
    def get_string(
        self,
        key: str,
        default: str,
    ) -> str:
        pass

    @overload
    def get_string(
        self,
        key: str,
        default: None = None,
    ) -> str | None:
        pass

    def get_string(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        value = self._values.get(key)
        if value is None or not value.strip():
            return default

        return value

    @overload
    def get_int(
        self,
        key: str,
        default: int,
    ) -> int:
        pass

    @overload
    def get_int(
        self,
        key: str,
        default: None = None,
    ) -> int | None:
        pass

    def get_int(
        self,
        key: str,
        default: int | None = None,
    ) -> int | None:
        value = self._values.get(key)
        if value is None or not value.strip():
            return default

        return int(value)

    @overload
    def get_int_list(
        self,
        key: str,
        default: list[int],
    ) -> list[int]:
        pass

    @overload
    def get_int_list(
        self,
        key: str,
        default: None = None,
    ) -> list[int] | None:
        pass

    def get_int_list(
        self,
        key: str,
        default: list[int] | None = None,
    ) -> list[int] | None:
        values = self._values.get(key)

        if values is None or not values.strip():
            return default

        return [int(value) for value in values.split(",")]


def _remove_none_values(data: dict[str, str | None]) -> dict[str, str]:
    for key, value in data.items():
        if value is None:
            del data[key]

    return cast(dict[str, str], data)


def _load_env(name: str | None) -> dict[str, str]:
    if not name:
        return _remove_none_values(dotenv_values(".env"))
    else:
        return _remove_none_values(dotenv_values(f".env.{name}"))


def load_env(names: Iterable[str]) -> Env:
    result = {**_load_env(None)}

    for name in names:
        result.update(_load_env(name))

    from os import environ

    result.update(environ)

    return Env(result)


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
        mailbox_name = env.get_string("MAIL_MAILBOX_NAME")
        token = env.get_string("MAIL_TOKEN")

        if not (mailbox_name and token):
            return None

        return cls(
            api_host=env.get_string(
                "MAIL_API_HOST",
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
        client_id = env.get_string("MASTODON_CLIENT_ID")
        client_secret = env.get_string("MASTODON_CLIENT_SECRET")
        source_account = env.get_string("MASTODON_SOURCE_ACCOUNT")
        if not (client_id and client_secret and source_account):
            return None

        return cls(
            api_base_url=env.get_string(
                "MASTODON_API_BASE_URL",
                "https://mastodon.social",
            ),
            client_id=client_id,
            client_secret=client_secret,
            source_account=source_account,
        )


@dataclass
class StateConfig:
    state_file: str | None

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            state_file=env.get_string("STATE_FILE_PATH"),
        )


@dataclass
class TelegramConfig:
    target_chat: int
    token: str
    upload_chat: int

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        target_chat = env.get_int("TELEGRAM_TARGET_CHAT_ID")
        token = env.get_string("TELEGRAM_TOKEN")
        upload_chat = env.get_int("TELEGRAM_UPLOAD_CHAT_ID")

        if not (target_chat and token and upload_chat):
            return None

        return cls(
            target_chat=target_chat,
            token=token,
            upload_chat=upload_chat,
        )


@dataclass
class TwitterConfig:
    source_account: str
    token: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        source_account = env.get_string("TWITTER_SOURCE_ACCOUNT")
        token = env.get_string("TWITTER_TOKEN")

        if not (source_account and token):
            return None

        return cls(
            source_account=source_account,
            token=token,
        )


@dataclass
class Config:
    download: DownloadConfig
    mail: MailConfig | None
    mastodon: MastodonConfig | None
    sanitizer: HtmlSanitizerConfig
    sentry: SentryConfig
    state: StateConfig
    telegram: TelegramConfig | None
    twitter: TwitterConfig | None

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            download=DownloadConfig.from_env(env),
            mail=MailConfig.from_env(env),
            mastodon=MastodonConfig.from_env(env),
            sanitizer=HtmlSanitizerConfig.from_env(env),
            sentry=SentryConfig.from_env(env),
            state=StateConfig.from_env(env),
            telegram=TelegramConfig.from_env(env),
            twitter=TwitterConfig.from_env(env),
        )
