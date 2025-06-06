import logging
import sys
from collections.abc import Coroutine
from typing import Any

import click
import uvloop

from twittergram.application import Application
from twittergram.init import initialize

_LOG = logging.getLogger(__name__)


@click.group
@click.pass_context
@click.option("--env", multiple=True)
def main(context: click.Context, env: list[str]) -> None:
    context.obj = initialize(env)


def _run_command(app: Application, command: Coroutine[Any, Any, Any]) -> None:
    async def __run() -> None:
        try:
            await command
        except Exception as e:
            _LOG.error("Got an exception", exc_info=e)
            sys.exit(1)
        finally:
            await app.close()

    uvloop.run(__run())


@main.command
@click.pass_obj
def forward_bluesky_posts(app: Application) -> None:
    _run_command(app, app.forward_bluesky_posts())


@main.command
@click.pass_obj
def forward_mails(app: Application) -> None:
    _run_command(app, app.forward_mails())


@main.command
@click.pass_obj
def forward_reddit_posts(app: Application) -> None:
    _run_command(app, app.forward_reddit_posts())


@main.command
@click.pass_obj
def forward_rss_feed(app: Application) -> None:
    _run_command(app, app.forward_rss_feed())


@main.command
@click.pass_obj
def forward_toots(app: Application) -> None:
    _run_command(app, app.forward_toots())


@main.command
@click.pass_obj
def forward_xcode(app: Application) -> None:
    _run_command(app, app.forward_xcode())


if __name__ == "__main__":
    main()
