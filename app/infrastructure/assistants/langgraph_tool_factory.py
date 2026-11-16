from langchain_core.tools import StructuredTool
from langgraph.types import interrupt

from ...application.errors.tool_rejected import ToolRejected
from ...application.ports.tool_gateway import ToolGateway
from ...domain.entities.tool_spec import ToolSpec


class LangGraphToolFactory:
    def __init__(self, gateway: ToolGateway):
        self.gateway = gateway

    def build_all(self, specs, token):
        return [self.build(spec, token) for spec in specs]

    def build(self, spec: ToolSpec, token):
        def run(**arguments):
            if spec.write and not self._approved(spec, arguments):
                return "El usuario canceló la operación"
            try:
                return self.gateway.call_tool(token, spec.name, arguments)
            except ToolRejected as e:
                return f"Error: {e}"

        return StructuredTool.from_function(
            func=run,
            name=spec.name,
            description=spec.description,
            args_schema=spec.input_schema,
        )

    def _approved(self, spec, arguments):
        args = ", ".join(f"{key}={value}" for key, value in arguments.items())
        decision = interrupt({
            "tool": spec.name,
            "arguments": arguments,
            "summary": f"{spec.name}({args})",
        })
        return decision["approved"]
