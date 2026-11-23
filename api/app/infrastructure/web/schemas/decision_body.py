from pydantic import BaseModel


class DecisionBody(BaseModel):
    interrupt_id: str
    approved: bool
