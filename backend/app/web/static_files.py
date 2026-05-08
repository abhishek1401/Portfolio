from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import mimetypes


@dataclass(frozen=True)
class StaticAsset:
    body: bytes
    mime_type: str


class StaticFileService:
    def __init__(self, root: Path):
        self.root = root

    def load(self, request_path: str) -> Optional[StaticAsset]:
        relative_path = self.relative_path(request_path)
        candidate = (self.root / relative_path).resolve()

        try:
            candidate.relative_to(self.root.resolve())
        except ValueError:
            return None

        if not candidate.is_file():
            return None

        mime_type = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
        return StaticAsset(body=candidate.read_bytes(), mime_type=mime_type)

    def relative_path(self, request_path: str) -> str:
        if request_path in {"/", "/public", "/admin"} or request_path.startswith("/profile/"):
            return "index.html"
        return request_path.lstrip("/")
