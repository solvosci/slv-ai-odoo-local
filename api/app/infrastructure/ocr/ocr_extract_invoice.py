import base64
import io

import pytesseract
from PIL import Image as PILImage
from PIL import ImageOps

from ...application.ports.extract_invoice_data import ExtractInvoiceData
from ...domain.entities.image import Image

SCALE_FACTOR = 2
THRESHOLD = 150
OCR_LANGUAGES = "spa+eng"

class OcrExtractInvoice(ExtractInvoiceData):
    def extract_invoice_data(self, image: Image) -> dict:
        processed = self._preprocess(self._to_pil(image))
        text = pytesseract.image_to_string(processed, lang=OCR_LANGUAGES)
        return {"text": text.strip()}

    def _to_pil(self, image: Image) -> PILImage.Image:
        raw = base64.b64decode(image.data)
        return PILImage.open(io.BytesIO(raw))

    # https://www.nutrient.io/blog/how-to-use-tesseract-ocr-in-python/
    def _preprocess(self, pil: PILImage.Image) -> PILImage.Image:
        gray = ImageOps.grayscale(pil)
        resized = gray.resize(
            (gray.width * SCALE_FACTOR, gray.height * SCALE_FACTOR),
            resample=PILImage.LANCZOS,
        )
        return resized.point(lambda pixel: 255 if pixel > THRESHOLD else 0)
