from injector import Injector

from twittergram.application import use_cases


class Application:
    def __init__(self, injector: Injector):
        self._injector = injector

    @property
    def forward_mails(self) -> use_cases.ForwardMails:
        return self._injector.get(use_cases.ForwardMails)

    @property
    def forward_reddit_posts(self) -> use_cases.ForwardRedditPosts:
        return self._injector.get(use_cases.ForwardRedditPosts)

    @property
    def forward_toots(self) -> use_cases.ForwardToots:
        return self._injector.get(use_cases.ForwardToots)

    @property
    def forward_xcode(self) -> use_cases.ForwardXcode:
        return self._injector.get(use_cases.ForwardXcode)
