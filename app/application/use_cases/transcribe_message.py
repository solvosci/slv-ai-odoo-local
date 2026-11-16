from dataclasses import dataclass

from ...domain.entities.transcription import Transcription
from ..errors.invalid_audio import InvalidAudio
from ..ports.transcriber import Transcriber


@dataclass
class TranscribeMessageUseCase:
    transcriber: Transcriber

    def execute(self, audio: bytes, language: str | None = None) -> Transcription:
        if not audio:
            raise InvalidAudio("The audio file is empty")
        return self.transcriber.transcribe(audio, language or None)
