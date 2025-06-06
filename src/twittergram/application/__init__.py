from dataclasses import dataclass

from injector import Injector, inject

from twittergram.application import repos, use_cases


@inject
@dataclass
class _StateAccess:
    repo: repos.StateRepo


class Application:
    def __init__(self, injector: Injector):
        self._injector = injector

    @property
    def forward_bluesky_posts(self) -> use_cases.ForwardBlueskyPosts:
        return self._injector.get(use_cases.ForwardBlueskyPosts)

    @property
    def forward_mails(self) -> use_cases.ForwardMails:
        return self._injector.get(use_cases.ForwardMails)

    @property
    def forward_reddit_posts(self) -> use_cases.ForwardRedditPosts:
        return self._injector.get(use_cases.ForwardRedditPosts)

    @property
    def forward_rss_feed(self) -> use_cases.ForwardRssFeed:
        return self._injector.get(use_cases.ForwardRssFeed)

    @property
    def forward_toots(self) -> use_cases.ForwardToots:
        return self._injector.get(use_cases.ForwardToots)

    @property
    def forward_xcode(self) -> use_cases.ForwardXcode:
        return self._injector.get(use_cases.ForwardXcode)

    async def close(self) -> None:
        state_access = self._injector.get(_StateAccess)
        await state_access.repo.close()
