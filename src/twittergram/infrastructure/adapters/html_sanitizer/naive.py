import re

from twittergram.application.ports import HtmlSanitizer


class NaiveHtmlSanitizer(HtmlSanitizer):
    IMG = re.compile(r"<img[^>]*>")
    SPAN = re.compile(r"<span[^>]*>")

    async def sanitize(self, raw: str) -> str:
        simple_sanitized = (
            raw.replace("<br />", "\n")
            .replace("<p>", "\n\n")
            .replace("</p>", "")
            .replace("</span>", "")
        )

        simple_sanitized = self.IMG.sub("", simple_sanitized)
        simple_sanitized = self.SPAN.sub("", simple_sanitized)

        return simple_sanitized.strip()
