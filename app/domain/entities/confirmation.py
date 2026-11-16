from dataclasses import dataclass


@dataclass(frozen=True)
class Confirmation:
    interrupt_id: str
    tool: str
    arguments: dict
    summary: str
