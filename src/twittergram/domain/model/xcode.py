from dataclasses import dataclass
from datetime import date

from .url import URL


@dataclass
class XcodeRelease:
    version_number: str
    version_build: str
    release_date: date
    release_notes: URL
