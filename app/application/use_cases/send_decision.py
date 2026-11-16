from dataclasses import dataclass

from ...domain.entities.decision import Decision
from ...domain.entities.reply import Reply
from ..ports.assistant import Assistant
from ..ports.conversation_lock import ConversationLock


@dataclass
class SendDecisionUseCase:
    assistant: Assistant
    lock: ConversationLock

    def execute(self, thread_id: str, token: str, decision: Decision) -> Reply:
        with self.lock.hold(thread_id):
            return self.assistant.resume(thread_id, decision, token)
