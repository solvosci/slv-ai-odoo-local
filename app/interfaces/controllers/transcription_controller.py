from dataclasses import dataclass

from ...application.use_cases.transcribe_message import TranscribeMessageUseCase
from ..presenters.transcription_presenter import TranscriptionPresenter


@dataclass
class TranscriptionController:
    transcribe_message_use_case: TranscribeMessageUseCase
    presenter: TranscriptionPresenter

    def handle_transcribe(self, audio: bytes, language: str | None = None) -> dict:
        transcription = self.transcribe_message_use_case.execute(audio, language)
        return self.presenter.present(transcription)
