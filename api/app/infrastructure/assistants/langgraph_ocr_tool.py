import pytesseract
from langchain_core.tools import StructuredTool

from ...application.ports.extract_invoice_data import ExtractInvoiceData
from ...domain.entities.image import Image

DESCRIPTION = (
    "Run OCR on the invoice image(s) or PDF pages attached to the current message and return its "
    "exact text. Use it whenever the attached image is an invoice and you need to "
    "read amounts, tax IDs, dates or line items. Do not use it for images that are "
    "not invoices. Never read those figures directly from the image."
)


def build_ocr_tool(extractor: ExtractInvoiceData, images: list[Image]) -> StructuredTool:
    def run():
        try:
            texts = [extractor.extract_invoice_data(image)["text"] for image in images]
        except (pytesseract.TesseractError, OSError) as e:
            return f"Error: no se pudo leer la imagen ({e})"

        if len(texts) == 1:
            return {"text": texts[0]}
        pages = [f"--- Página/imagen {n} ---\n{text}" for n, text in enumerate(texts, 1)]
        return {"text": "\n\n".join(pages)}

    return StructuredTool.from_function(
        func=run,
        name="extract_invoice_data",
        description=DESCRIPTION,
        args_schema={"type": "object", "properties": {}},
    )
