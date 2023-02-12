import asyncio

import click
from twittergram.application import Application
from twittergram.init import initialize


@click.group
@click.pass_context
@click.option("--env", multiple=True)
def main(context: click.Context, env: list[str]) -> None:
    context.obj = initialize(env)


@main.command
@click.pass_obj
def forward_mails(app: Application) -> None:
    asyncio.run(app.forward_mails())


@main.command
@click.pass_obj
def forward_toots(app: Application) -> None:
    asyncio.run(app.forward_toots())


@main.command
@click.pass_obj
def forward_tweets(app: Application) -> None:
    asyncio.run(app.forward_tweets())
