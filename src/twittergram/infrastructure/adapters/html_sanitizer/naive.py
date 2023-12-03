import re

from twittergram.application.ports import HtmlSanitizer


class NaiveHtmlSanitizer(HtmlSanitizer):
    SPAN = re.compile(r"<span[^>]*>")

    async def sanitize(self, raw: str) -> str:
        simple_sanitized = (
            raw.replace("<br />", "\n")
            .replace("<p>", "\n\n")
            .replace("</p>", "")
            .replace("</span>", "")
            .strip()
        )

        return self.SPAN.sub("", simple_sanitized)
