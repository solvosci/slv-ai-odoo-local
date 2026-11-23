from dataclasses import dataclass


@dataclass(frozen=True)
class Image:
    mime_type: str
    data: str
    name: str | None = None

    @property
    def data_url(self) -> str:
        return f"data:{self.mime_type};base64,{self.data}"
