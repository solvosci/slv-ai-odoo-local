from ...domain.entities.transcription import Transcription


class TranscriptionPresenter:
    def present(self, transcription: Transcription) -> dict:
        return {
            "text": transcription.text,
            "language": transcription.language,
        }
