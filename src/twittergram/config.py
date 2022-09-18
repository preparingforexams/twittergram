from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union

from dotenv import dotenv_values


class Env:
    def __init__(self, values: Dict[str, str]):
        self._values = values

    def get_string(
        self,
        key: str,
        default: Optional[str] = None,
        required: bool = True,
    ) -> Optional[str]:
        value = self._values.get(key, default)
        if required:
            if value is None:
                raise ValueError(f"Value for {key} is missing")
            if not value.strip():
                raise ValueError(f"Value for {key} is blank")

        return value

    def get_int(
        self,
        key: str,
        default: Optional[int] = None,
        required: bool = True,
    ) -> Optional[int]:
        value = self._values.get(key)
        if required and default is None:
            if value is None:
                raise ValueError(f"Value for {key} is missing")
            if not value.strip():
                raise ValueError(f"Value for {key} is blank")
        elif value is None or not value.strip() and default is not None:
            return default

        return int(value)

    def get_int_list(
        self,
        key: str,
        default: Optional[List[int]] = None,
        required: bool = True,
    ) -> Optional[List[int]]:
        values = self._values.get(key)
        if required and default is None:
            if values is None:
                raise ValueError(f"Value for {key} is missing")
            if not values.strip():
                raise ValueError(f"Value for {key} is blank")
        elif values is None or not values.strip() and default is not None:
            return default

        return [int(value) for value in values.split(",")]


def _load_env(name: str) -> dict:
    if not name:
        return dotenv_values(".env")
    else:
        return dotenv_values(f".env.{name}")


def load_env(names: Union[str, Tuple[str, ...]]) -> Env:
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
    release: str | None

    @classmethod
    def from_env(cls, env: Env) -> SentryConfig:
        return cls(
            dsn=env.get_string("SENTRY_DSN", required=False),
            release=env.get_string("APP_VERSION", default="debug"),
        )


@dataclass
class Config:
    sentry: SentryConfig
    state: StateConfig
    telegram: TelegramConfig
    twitter: TwitterConfig

    @classmethod
    def from_env(cls, env: Env) -> Config:
        return cls(
            sentry=SentryConfig.from_env(env),
            state=StateConfig.from_env(env),
            telegram=TelegramConfig.from_env(env),
            twitter=TwitterConfig.from_env(env),
        )


@dataclass
class StateConfig:
    state_file: str

    @classmethod
    def from_env(cls, env: Env) -> StateConfig:
        return cls(
            state_file=env.get_string("STATE_FILE_PATH"),
        )


@dataclass
class TelegramConfig:
    token: str

    @classmethod
    def from_env(cls, env: Env) -> TelegramConfig:
        return cls(
            token=env.get_string("TELEGRAM_TOKEN"),  # type: ignore
        )


@dataclass
class TwitterConfig:
    token: str

    @classmethod
    def from_env(cls, env: Env) -> TwitterConfig:
        return cls(
            token=env.get_string("TWITTER_TOKEN"),  # type: ignore
        )
