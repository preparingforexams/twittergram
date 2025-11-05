from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from .url import URL


@dataclass
class XcodeRelease:
    version_number: str
    version_build: str
    release_date: date
    release_notes: URL
