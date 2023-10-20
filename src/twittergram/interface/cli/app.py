import asyncio
import logging
import sys
from typing import Any, Coroutine

import click

from twittergram.application import Application
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
def forward_mails(app: Application) -> None:
    _run_command(app.forward_mails())


@main.command
@click.pass_obj
def forward_reddit_posts(app: Application) -> None:
    _run_command(app.forward_reddit_posts())


@main.command
@click.pass_obj
def forward_toots(app: Application) -> None:
    _run_command(app.forward_toots())


@main.command
@click.pass_obj
def forward_tweets(app: Application) -> None:
    _run_command(app.forward_tweets())


@main.command
@click.pass_obj
def forward_xcode(app: Application) -> None:
    _run_command(app.forward_xcode())
