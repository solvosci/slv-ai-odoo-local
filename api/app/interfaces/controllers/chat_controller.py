from dataclasses import dataclass

from ...application.use_cases.send_decision import SendDecisionUseCase
from ...application.use_cases.send_message import SendMessageUseCase
from ...domain.entities.decision import Decision
from ...domain.entities.image import Image
from ..presenters.chat_presenter import ChatPresenter


@dataclass
class ChatController:
    send_message_use_case: SendMessageUseCase
    send_decision_use_case: SendDecisionUseCase
    presenter: ChatPresenter

    def handle_chat(self, request_data: dict) -> dict:
        if request_data.get("decision"):
            reply = self._decide(request_data)
        else:
            reply = self._message(request_data)
        return self.presenter.present(reply)

    def _message(self, data):
        images = [
            Image(mime_type=i["type"], data=i["data"], name=i.get("name"))
            for i in data.get("images") or []
        ]
        return self.send_message_use_case.execute(
            data["thread_id"], data["token"], data.get("message") or "", images)

    def _decide(self, data):
        decision = Decision(**data["decision"])
        return self.send_decision_use_case.execute(
            data["thread_id"], data["token"], decision)
