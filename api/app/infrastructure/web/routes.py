from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from ...application.errors.invalid_audio import InvalidAudio
from ...application.errors.service_unavailable import ServiceUnavailable
from ...interfaces.controllers.chat_controller import ChatController
from ...interfaces.controllers.transcription_controller import TranscriptionController
from ..pdf.pdf_pages import InvalidPdf, pdf_to_page_images
from .schemas.chat_request import ChatRequest

PDF_TYPE = "application/pdf"


def expand_pdfs(data: dict) -> dict:
    images = []
    for image in data.get("images") or []:
        if image["type"] == PDF_TYPE:
            images += pdf_to_page_images(image["data"], image.get("name"))
        else:
            images.append(image)
    return {**data, "images": images}


def create_router(
    controller: ChatController,
    transcription_controller: TranscriptionController,
    transcribe_max_bytes: int,
) -> APIRouter:
    router = APIRouter()

    @router.post("/chat")
    def chat(request: ChatRequest):
        try:
            return controller.handle_chat(expand_pdfs(request.model_dump()))
        except InvalidPdf as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ServiceUnavailable as e:
            raise HTTPException(status_code=502, detail=str(e)) from e

    @router.post("/transcribe")
    async def transcribe(
        file: Annotated[UploadFile, File()],
        language: Annotated[str | None, Form()] = None,
    ):
        audio = await file.read(transcribe_max_bytes + 1)
        if len(audio) > transcribe_max_bytes:
            raise HTTPException(status_code=413, detail="Audio file is too large")
        try:
            return await run_in_threadpool(
                transcription_controller.handle_transcribe, audio, language)
        except InvalidAudio as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ServiceUnavailable as e:
            raise HTTPException(status_code=503, detail=str(e)) from e

    return router
