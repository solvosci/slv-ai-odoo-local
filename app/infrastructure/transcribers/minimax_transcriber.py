import io

import requests
from langsmith import traceable
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from ...application.errors.invalid_audio import InvalidAudio
from ...application.errors.service_unavailable import ServiceUnavailable
from ...application.ports.transcriber import Transcriber
from ...domain.entities.transcription import Transcription


class MiniMaxTranscriber(Transcriber):

    def __init__(self, api_key, base_url="https://api.minimax.io/v1",
                 model="asr-1.0", default_language=None, timeout=120):
        self._url = base_url.rstrip("/") + "/speech_to_text"
        self._api_key = api_key
        self._model = model
        self._default_language = default_language
        self._timeout = timeout

    @traceable(name="minimax.transcribe")
    def transcribe(self, audio: bytes, language: str | None = None) -> Transcription:
        language = language or self._default_language
        wav = self._to_wav(audio)
        headers = {"Authorization": f"Bearer {self._api_key}"}
        if language:
            headers["language"] = language
        try:
            response = requests.post(
                self._url,
                headers=headers,
                data={"model": self._model},
                files={"file": ("audio.wav", wav, "audio/wav")},
                timeout=self._timeout,
            )
        except requests.RequestException as e:
            raise ServiceUnavailable(f"MiniMax ASR unavailable: {e}") from e

        if response.status_code >= 400:
            try:
                message = response.json()["error"]["message"]
            except (ValueError, KeyError, TypeError):
                message = f"Error {response.status_code}"
            if response.status_code in (400, 413, 422):
                raise InvalidAudio(message)
            raise ServiceUnavailable(f"MiniMax ASR {response.status_code}: {message}")

        text = response.json().get("text", "").strip()
        return Transcription(text=text, language=language or "auto")

    def _to_wav(self, audio: bytes) -> bytes:
        try:
            segment = AudioSegment.from_file(io.BytesIO(audio))
        except (CouldntDecodeError, IndexError) as e:
            raise InvalidAudio("The file is not a valid or supported audio") from e
        wav = io.BytesIO()
        segment.set_frame_rate(16000).set_channels(1).set_sample_width(2).export(wav, format="wav")
        return wav.getvalue()
