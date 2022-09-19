from dataclasses import dataclass

from injector import inject

from twittergram.application import use_cases


@inject
@dataclass
class Application:
    forward_tweets: use_cases.ForwardTweets
