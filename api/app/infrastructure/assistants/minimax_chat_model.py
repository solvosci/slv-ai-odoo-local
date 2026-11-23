from langchain_openai import ChatOpenAI

from .leak_retry import agenerate_without_leak, generate_without_leak


class MiniMaxChatModel(ChatOpenAI):
    """ChatOpenAI que reintenta cuando MiniMax filtra una llamada a herramienta como texto,
    para que la respuesta rotano llegue al historial de la conversación."""

    def _generate(self, *args, **kwargs):
        return generate_without_leak(super()._generate, *args, **kwargs)

    async def _agenerate(self, *args, **kwargs):
        return await agenerate_without_leak(super()._agenerate, *args, **kwargs)
