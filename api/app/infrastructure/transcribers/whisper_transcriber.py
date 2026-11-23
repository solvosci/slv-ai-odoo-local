import io
import threading

from faster_whisper import WhisperModel
from langsmith import traceable

from ...application.errors.invalid_audio import InvalidAudio
from ...application.errors.service_unavailable import ServiceUnavailable
from ...application.ports.transcriber import Transcriber
from ...domain.entities.transcription import Transcription


class WhisperTranscriber(Transcriber):

    def __init__(self, model_size="medium", device="cpu", compute_type="int8",
                 default_language=None, beam_size=5, vad_filter=True):
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._default_language = default_language
        self._beam_size = beam_size
        self._vad_filter = vad_filter
        self._model = None
        self._load_lock = threading.Lock()

    def _get_model(self):
        with self._load_lock:
            if self._model is None:
                try:
                    self._model = WhisperModel(
                        self._model_size,
                        device=self._device,
                        compute_type=self._compute_type,
                    )
                except Exception as e:
                    raise ServiceUnavailable(f"Could not load Whisper model: {e}") from e
            return self._model

    @traceable(name="whisper.transcribe")
    def transcribe(self, audio: bytes, language: str | None = None) -> Transcription:
        model = self._get_model()
        try:
            segments, info = model.transcribe(
                io.BytesIO(audio),
                language=language or self._default_language,
                beam_size=self._beam_size,
                vad_filter=self._vad_filter,
            )
            text = " ".join(s.text.strip() for s in segments).strip()
        except ValueError as e:
            raise InvalidAudio(f"Unsupported language or parameters: {e}") from e
        except Exception as e:
            if type(e).__module__.startswith("av"):
                raise InvalidAudio("The file is not a valid or supported audio") from e
            raise
        return Transcription(text=text, language=info.language)
