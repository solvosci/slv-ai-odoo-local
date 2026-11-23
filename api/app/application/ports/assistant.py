from abc import ABC, abstractmethod

from ...domain.entities.decision import Decision
from ...domain.entities.image import Image
from ...domain.entities.reply import Reply


class Assistant(ABC):
    @abstractmethod
    def reply(self, thread_id: str, message: str, token: str,
              images: list[Image] | None = None) -> Reply: ...

    @abstractmethod
    def resume(self, thread_id: str, decision: Decision, token: str) -> Reply: ...
