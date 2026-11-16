from pydantic import BaseModel, Field, model_validator

from .decision_body import DecisionBody
from .image_body import ImageBody


MAX_IMAGES = 5


class ChatRequest(BaseModel):
    thread_id: str
    token: str

    message: str | None = None
    images: list[ImageBody] = Field(default_factory=list, max_length=MAX_IMAGES)
    decision: DecisionBody | None = None

    @model_validator(mode="after")
    def exactly_one(self):
        has_message = bool(self.message) or bool(self.images)
        if has_message == (self.decision is not None):
            raise ValueError("Send exactly one of 'message'/'images' or 'decision'")
        return self
