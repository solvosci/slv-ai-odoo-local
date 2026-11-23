from abc import ABC, abstractmethod

from ...domain.entities.tool_spec import ToolSpec


class ToolGateway(ABC):
    @abstractmethod
    def list_tools(self, token: str) -> list[ToolSpec]: ...

    @abstractmethod
    def call_tool(self, token: str, name: str, arguments: dict) -> dict: ...
