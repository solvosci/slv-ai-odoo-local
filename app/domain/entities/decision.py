from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    interrupt_id: str
    approved: bool
