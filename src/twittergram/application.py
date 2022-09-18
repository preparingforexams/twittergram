from dataclasses import dataclass

from twittergram.forward_tweets import ForwardTweets


@dataclass
class Application:
    forward_tweets: ForwardTweets
