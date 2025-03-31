import asyncio
import logging
import sys
from collections.abc import Coroutine
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
from injector import inject

from twittergram.application import Application, repos
from twittergram.application.model import state
from twittergram.init import initialize

_LOG = logging.getLogger(__name__)


@click.group
@click.pass_context
@click.option("--env", multiple=True)
def main(context: click.Context, env: list[str]) -> None:
    context.obj = initialize(env)


def _run_command(command: Coroutine[Any, Any, Any]) -> None:
    try:
        asyncio.run(command)
    except Exception as e:
        _LOG.error("Got an exception", exc_info=e)
        sys.exit(1)


@main.command
@click.pass_obj
def forward_bluesky_posts(app: Application) -> None:
    _run_command(app.forward_bluesky_posts())


@main.command
@click.pass_obj
def forward_mails(app: Application) -> None:
    _run_command(app.forward_mails())


@main.command
@click.pass_obj
def forward_reddit_posts(app: Application) -> None:
    _run_command(app.forward_reddit_posts())


@main.command
@click.pass_obj
def forward_rss_feed(app: Application) -> None:
    _run_command(app.forward_rss_feed())


@main.command
@click.pass_obj
def forward_toots(app: Application) -> None:
    _run_command(app.forward_toots())


@main.command
@click.pass_obj
def forward_xcode(app: Application) -> None:
    _run_command(app.forward_xcode())


@main.command
@click.pass_obj
@click.option(
    "file_path",
    "--from-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
)
@click.option(
    "type_name",
    "--type",
    type=str,
    required=True,
)
def copy_state(app: Application, file_path: Path, type_name: str) -> None:
    try:
        state_type = getattr(state, type_name)
    except AttributeError:
        _LOG.error("No such State type: %s", type_name)
        sys.exit(1)

    if not issubclass(state_type, state.State):
        _LOG.error("%s is not a State subtype", type_name)
        sys.exit(1)

    state_access = app._injector.get(StateAccess)
    asyncio.run(_transfer_state(state_access.repo, state_type, file_path))


@inject
@dataclass
class StateAccess:
    repo: repos.StateRepo


async def _transfer_state(
    target_storage: repos.StateRepo,
    state_type: type[state.State],
    file_path: Path,
) -> None:
    from bs_state.implementation import file_storage

    initial_state = state_type.initial()
    source_storage = await file_storage.load(
        initial_state=initial_state,
        file=file_path,
    )

    old_state = await source_storage.load()
    if old_state == initial_state:
        _LOG.error("Not transferring state since it matches initial state")
        sys.exit(1)

    await target_storage.store_state(old_state)


if __name__ == "__main__":
    main()
