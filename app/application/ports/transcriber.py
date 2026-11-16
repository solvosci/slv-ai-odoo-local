from abc import ABC, abstractmethod

from ...domain.entities.transcription import Transcription


class Transcriber(ABC):
    @abstractmethod
    def transcribe(self, audio: bytes, language: str | None = None) -> Transcription: ...
