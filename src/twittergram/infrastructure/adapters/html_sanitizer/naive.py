import logging
import re

from twittergram.application.ports import HtmlSanitizer

_LOG = logging.getLogger(__name__)


class NaiveHtmlSanitizer(HtmlSanitizer):
    IMG = re.compile(r"<img[^>]*>")
    SPAN = re.compile(r"<span[^>]*>")
    MESSAGE = re.compile(r"<[Mm]essage( type=\"(?P<type>\w+)\")?>")
    TR = re.compile(r"<tr[^>]*>")
    TD = re.compile(r"<td[^>]*>")

    @staticmethod
    def _choose_emoji(message_type: str | None) -> str:
        match message_type:
            case "important":
                return "⚠️"
            case "note":
                return "ℹ️"
            case None:
                return ""
            case other:
                _LOG.error("Unknown HTML message type: %s", other)
                return ""

    def _replace_message(self, match: re.Match[str]) -> str:
        message_type = match.group("type")

        emoji = self._choose_emoji(message_type)
        return f"\n{emoji * 3}"

    async def sanitize(self, raw: str) -> str:
        simple_sanitized = (
            raw.replace("<br />", "\n")
            .replace("<p>", "\n\n")
            .replace("</p>", "")
            .replace("</span>", "")
            .replace("<ul>", "")
            .replace("</ul>", "")
            .replace("<li>", "- ")
            .replace("</li>", "")
            .replace("<h1>", "<b>")
            .replace("</h1>", "</b>")
            .replace("<h2>", "<b>")
            .replace("</h2>", "</b>")
            .replace("<h3>", "<b>")
            .replace("</h3>", "</b>")
            .replace("</Message>", "\n")
            .replace("<table>", "")
            .replace("</table>", "")
            .replace("</td>", "")
            .replace("</tr>", "")
        )

        simple_sanitized = self.TD.sub("- ", simple_sanitized)
        simple_sanitized = self.TR.sub("", simple_sanitized)
        simple_sanitized = self.IMG.sub("", simple_sanitized)
        simple_sanitized = self.SPAN.sub("", simple_sanitized)
        simple_sanitized = self.MESSAGE.sub(
            repl=self._replace_message,
            string=simple_sanitized,
        )

        return simple_sanitized.strip()
