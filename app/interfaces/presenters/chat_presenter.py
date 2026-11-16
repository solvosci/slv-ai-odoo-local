from ...domain.entities.reply import Reply


class ChatPresenter:
    def present(self, reply: Reply) -> dict:
        confirmation = reply.confirmation
        return {
            "type": reply.type,
            "reply": reply.text,
            "confirmation": vars(confirmation) if confirmation else None,
        }
