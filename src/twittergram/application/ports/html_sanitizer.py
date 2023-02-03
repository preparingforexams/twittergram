import abc


class HtmlSanitizer(abc.ABC):
    @abc.abstractmethod
    async def sanitize(self, raw: str) -> str:
        pass
