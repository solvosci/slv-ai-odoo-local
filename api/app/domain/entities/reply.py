from dataclasses import dataclass
from typing import Literal

from .confirmation import Confirmation


@dataclass(frozen=True)
class Reply:
    type: Literal["message", "confirmation"]
    text: str | None = None
    confirmation: Confirmation | None = None

    @classmethod
    def message(cls, text):
        return cls(type="message", text=text)

    @classmethod
    def confirm(cls, confirmation):
        return cls(type="confirmation", confirmation=confirmation)
