from twittergram.application.ports import HtmlSanitizer


class NaiveHtmlSanitizer(HtmlSanitizer):
    async def sanitize(self, raw: str) -> str:
        return (
            raw.replace("<br />", "\n")
            .replace("<p>", "\n\n")
            .replace("</p>", "")
            .strip()
        )
