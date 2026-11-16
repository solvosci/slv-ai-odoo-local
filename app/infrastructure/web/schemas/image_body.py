import base64
import binascii

from pydantic import BaseModel, field_validator

ALLOWED_IMAGE_TYPES = ("image/png", "image/jpeg", "image/webp")
MAX_IMAGE_BYTES = 5 * 1024 * 1024


class ImageBody(BaseModel):
    type: str
    data: str
    name: str | None = None

    @field_validator("type")
    @classmethod
    def allowed_type(cls, value):
        if value not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Unsupported image type {value!r}")
        return value


    @field_validator("data")
    @classmethod
    def valid_base64(cls, value):
        try:
            raw = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as e:
            raise ValueError("Image data must be base64 encoded") from e
        if not raw:
            raise ValueError("Image is empty")
        if len(raw) > MAX_IMAGE_BYTES:
            raise ValueError("Image is too large")
        return value
