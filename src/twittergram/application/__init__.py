from injector import Injector

from twittergram.application import use_cases


class Application:
    def __init__(self, injector: Injector):
        self._injector = injector

    @property
    def forward_tweets(self) -> use_cases.ForwardTweets:
        return self._injector.get(use_cases.ForwardTweets)

    @property
    def forward_toots(self) -> use_cases.ForwardToots:
        return self._injector.get(use_cases.ForwardToots)
