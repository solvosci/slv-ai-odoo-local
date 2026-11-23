from dataclasses import dataclass

from langchain_ollama import ChatOllama

from ...application.ports.assistant import Assistant
from ...application.ports.conversation_lock import ConversationLock
from ...application.ports.tool_gateway import ToolGateway
from ...application.ports.transcriber import Transcriber
from ...application.use_cases.send_decision import SendDecisionUseCase
from ...application.use_cases.send_message import SendMessageUseCase
from ...application.use_cases.transcribe_message import TranscribeMessageUseCase
from ...interfaces.controllers.chat_controller import ChatController
from ...interfaces.controllers.transcription_controller import TranscriptionController
from ...interfaces.presenters.chat_presenter import ChatPresenter
from ...interfaces.presenters.transcription_presenter import TranscriptionPresenter
from ..assistants.langgraph_assistant import LangGraphAssistant
from ..assistants.minimax_chat_model import MiniMaxChatModel
from ..gateways.odoo_tool_gateway import OdooToolGateway
from ..locking.memory_conversation_lock import MemoryConversationLock
from ..ocr.ocr_extract_invoice import OcrExtractInvoice
from . import settings


@dataclass
class Application:
    tool_gateway: ToolGateway
    assistant: Assistant
    lock: ConversationLock
    transcriber: Transcriber

    def __post_init__(self):
        self.send_message_use_case = SendMessageUseCase(self.assistant, self.lock)
        self.send_decision_use_case = SendDecisionUseCase(self.assistant, self.lock)
        self.chat_controller = ChatController(
            send_message_use_case=self.send_message_use_case,
            send_decision_use_case=self.send_decision_use_case,
            presenter=ChatPresenter(),
        )
        self.transcribe_message_use_case = TranscribeMessageUseCase(self.transcriber)
        self.transcription_controller = TranscriptionController(
            transcribe_message_use_case=self.transcribe_message_use_case,
            presenter=TranscriptionPresenter(),
        )


def create_application() -> Application:
    gateway = OdooToolGateway(settings.ODOO_URL, settings.ODOO_TIMEOUT)

    model = MiniMaxChatModel(
        model=settings.MINIMAX_MODEL,
        base_url=settings.MINIMAX_BASE_URL,
        api_key=settings.MINIMAX_API_KEY,
        temperature=settings.MINIMAX_TEMPERATURE,
        max_tokens=settings.MINIMAX_MAX_TOKENS,
        timeout=settings.MINIMAX_TIMEOUT,
    )

    # model = ChatOllama(
    #     model=settings.OLLAMA_MODEL,
    #     base_url=settings.OLLAMA_BASE_URL,
    #     temperature=settings.OLLAMA_TEMPERATURE,
    #     top_p=settings.OLLAMA_TOP_P,
    #     top_k=settings.OLLAMA_TOP_K,
    #     repeat_penalty=settings.OLLAMA_REPEAT_PENALTY,
    #     num_ctx=settings.OLLAMA_NUM_CTX,
    #     num_predict=settings.OLLAMA_NUM_PREDICT,
    #     keep_alive=settings.OLLAMA_KEEP_ALIVE,
    #     reasoning=False,
    # )
    return Application(
        tool_gateway=gateway,
        assistant=LangGraphAssistant(
            model, gateway, settings.SYSTEM_PROMPT, OcrExtractInvoice()
        ),
        lock=MemoryConversationLock(),
        transcriber=create_transcriber(),
    )


def create_transcriber() -> Transcriber:
    if settings.TRANSCRIBER == "minimax":
        from ..transcribers.minimax_transcriber import MiniMaxTranscriber

        return MiniMaxTranscriber(
            api_key=settings.MINIMAX_API_KEY,
            base_url=settings.MINIMAX_BASE_URL,
            model=settings.MINIMAX_ASR_MODEL,
            default_language=settings.TRANSCRIBE_LANGUAGE,
            timeout=settings.MINIMAX_ASR_TIMEOUT,
        )
    if settings.TRANSCRIBER == "whisper":
        from ..transcribers.whisper_transcriber import WhisperTranscriber

        return WhisperTranscriber(
            model_size=settings.WHISPER_MODEL,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
            default_language=settings.TRANSCRIBE_LANGUAGE,
            beam_size=settings.WHISPER_BEAM_SIZE,
            vad_filter=settings.WHISPER_VAD_FILTER,
        )
    raise ValueError(f"Unknown TRANSCRIBER: {settings.TRANSCRIBER!r} (use 'whisper' or 'minimax')")
