import re

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langsmith import traceable

from ...application.ports.assistant import Assistant
from ...application.ports.tool_gateway import ToolGateway
from ...domain.entities.confirmation import Confirmation
from ...domain.entities.reply import Reply
from .langgraph_tool_factory import LangGraphToolFactory

ALREADY_PROCESSED = "Esa acción ya se procesó."
PENDING_ACTION = "Tienes una acción pendiente de confirmar o cancelar."
THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)


class LangGraphAssistant(Assistant):
    def __init__(self, model, gateway: ToolGateway, system_prompt, checkpointer=None):
        self.model = model
        self.gateway = gateway
        self.tool_factory = LangGraphToolFactory(gateway)
        self.system_prompt = system_prompt
        self.checkpointer = checkpointer or MemorySaver()

    @traceable(name="assistant.reply")
    def reply(self, thread_id, message, token, images=None):
        graph = self._build_graph(token)
        config = {"configurable": {"thread_id": thread_id}}
        if self._pending(graph, config):
            return Reply.message(PENDING_ACTION)
        graph.invoke({"messages": [self._human_message(message, images)]}, config)
        return self._to_reply(graph, config)

    @traceable(name="assistant.resume")
    def resume(self, thread_id, decision, token):
        graph = self._build_graph(token)
        config = {"configurable": {"thread_id": thread_id}}
        pending = self._pending(graph, config)
        if not pending or pending.id != decision.interrupt_id:
            return Reply.message(ALREADY_PROCESSED)
        graph.invoke(Command(resume={"approved": decision.approved}), config)
        return self._to_reply(graph, config)

    def _build_graph(self, token):
        specs = self.gateway.list_tools(token)
        return create_agent(
            self.model,
            self.tool_factory.build_all(specs, token),
            system_prompt=self.system_prompt,
            checkpointer=self.checkpointer,
        )

    def _human_message(self, message, images):
        if not images:
            return HumanMessage(message)
        content = [{"type": "text", "text": message}] if message else []
        content += [
            {"type": "image_url", "image_url": {"url": image.data_url}}
            for image in images
        ]
        return HumanMessage(content=content)

    def _pending(self, graph, config):
        interrupts = graph.get_state(config).interrupts
        return interrupts[0] if interrupts else None

    def _to_reply(self, graph, config):
        pending = self._pending(graph, config)
        if pending:
            return Reply.confirm(Confirmation(interrupt_id=pending.id, **pending.value))
        last = graph.get_state(config).values["messages"][-1]
        return Reply.message(THINK_BLOCK.sub("", last.text).strip())
