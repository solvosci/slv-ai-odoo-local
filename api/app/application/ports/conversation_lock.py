from abc import ABC, abstractmethod
from contextlib import AbstractContextManager


class ConversationLock(ABC):
    # https://docs.python.org/3/library/contextlib.html
    @abstractmethod
    def hold(self, thread_id: str) -> AbstractContextManager: ...
