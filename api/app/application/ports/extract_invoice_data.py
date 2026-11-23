from abc import ABC, abstractmethod

from ...domain.entities.image import Image


class ExtractInvoiceData(ABC):
    @abstractmethod
    def extract_invoice_data(self, image: Image) -> dict: ...
