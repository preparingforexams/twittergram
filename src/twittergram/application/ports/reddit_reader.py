import abc


class RedditReader(abc.ABC):
    @abc.abstractmethod
    async def lookup_user_id(self, name: str) -> str:
        pass
