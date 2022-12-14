import asyncio

import click

from twittergram.application import Application
from twittergram.init import initialize


@click.group
@click.pass_context
def main(context: click.Context):
    context.obj = initialize()


@main.command
@click.pass_obj
def forward_tweets(app: Application):
    asyncio.run(app.forward_tweets())
