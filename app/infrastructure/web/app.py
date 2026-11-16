from fastapi import FastAPI

from ..configuration import settings
from ..configuration.container import Application
from .routes import create_router


def create_web_app(application: Application) -> FastAPI:
    app = FastAPI(title="Solvy API")
    app.include_router(create_router(
        application.chat_controller,
        application.transcription_controller,
        settings.TRANSCRIBE_MAX_BYTES,
    ))
    return app
