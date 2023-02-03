from __future__ import annotations

from dataclasses import dataclass
from typing import overload

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


def _load_env(name: str) -> dict:
    if not name:
        return dotenv_values(".env")
    else:
        return dotenv_values(f".env.{name}")


def load_env(names: str | tuple[str, ...]) -> Env:
    result = {}

    if isinstance(names, str):
        result.update(_load_env(names))
    elif isinstance(names, tuple):
        for name in names:
            result.update(_load_env(name))
    else:
        raise ValueError(f"Invalid .env names: {names}")

    from os import environ

    result.update(environ)

    return Env(result)


@dataclass
class SentryConfig:
    dsn: str | None
    release: str

    @classmethod
    def from_env(cls, env: Env) -> SentryConfig:
        return cls(
            dsn=env.get_string("SENTRY_DSN"),
            release=env.get_string("APP_VERSION", default="debug"),
        )


@dataclass
class Config:
    download: DownloadConfig
    sentry: SentryConfig
    state: StateConfig
    telegram: TelegramConfig | None
    twitter: TwitterConfig | None

    @classmethod
    def from_env(cls, env: Env) -> Config:
        return cls(
            download=DownloadConfig.from_env(env),
            sentry=SentryConfig.from_env(env),
            state=StateConfig.from_env(env),
            telegram=TelegramConfig.from_env(env),
            twitter=TwitterConfig.from_env(env),
        )


@dataclass
class DownloadConfig:
    download_directory: str

    @classmethod
    def from_env(cls, env: Env) -> DownloadConfig:
        return cls(
            download_directory=env.get_string(
                "DOWNLOAD_DIR",
                default="/tmp/twittergram",
            ),
        )


@dataclass
class StateConfig:
    state_file: str | None

    @classmethod
    def from_env(cls, env: Env) -> StateConfig:
        return cls(
            state_file=env.get_string("STATE_FILE_PATH"),
        )


@dataclass
class TelegramConfig:
    target_chat: int
    token: str
    upload_chat: int

    @classmethod
    def from_env(cls, env: Env) -> TelegramConfig | None:
        token = env.get_string("TELEGRAM_TOKEN")
        if not token:
            return None
        return cls(
            target_chat=env.get_int(
                "TELEGRAM_TARGET_CHAT_ID",
                default=133399998,
            ),
            token=token,
            upload_chat=env.get_int(
                "TELEGRAM_UPLOAD_CHAT_ID",
                default=1259947317,
            ),
        )


@dataclass
class TwitterConfig:
    source_account: str
    token: str

    @classmethod
    def from_env(cls, env: Env) -> TwitterConfig | None:
        source_account = env.get_string("TWITTER_SOURCE_ACCOUNT")
        token = env.get_string("TWITTER_TOKEN")

        if not (source_account and token):
            return None

        return cls(
            source_account=source_account,
            token=token,
        )
