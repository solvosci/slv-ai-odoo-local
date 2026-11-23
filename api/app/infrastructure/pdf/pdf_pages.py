import base64
import io

import pypdfium2 as pdfium

MAX_PDF_PAGES = 5
RENDER_SCALE = 2.5


class InvalidPdf(ValueError):
    pass


def pdf_to_page_images(data_b64: str, name: str | None = None) -> list[dict]:
    try:
        pdf = pdfium.PdfDocument(base64.b64decode(data_b64))
    except (pdfium.PdfiumError, ValueError) as e:
        raise InvalidPdf("No se pudo leer el PDF") from e
    try:
        pages = []
        for index in range(min(len(pdf), MAX_PDF_PAGES)):
            buffer = io.BytesIO()
            pdf[index].render(scale=RENDER_SCALE).to_pil().save(buffer, format="PNG")
            pages.append({
                "type": "image/png",
                "data": base64.b64encode(buffer.getvalue()).decode(),
                "name": f"{name or 'document'} - p{index + 1}",
            })
        return pages
    finally:
        pdf.close()
