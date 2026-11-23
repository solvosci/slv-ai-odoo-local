from dataclasses import dataclass

from ...domain.entities.image import Image
from ...domain.entities.reply import Reply
from ..ports.assistant import Assistant
from ..ports.conversation_lock import ConversationLock


@dataclass
class SendMessageUseCase:
    assistant: Assistant
    lock: ConversationLock

    def execute(self, thread_id: str, token: str, message: str,
                images: list[Image] | None = None) -> Reply:
        with self.lock.hold(thread_id):
            return self.assistant.reply(thread_id, message, token, images or [])
