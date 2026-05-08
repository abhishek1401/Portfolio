from pathlib import Path
from typing import Optional
import mimetypes
import secrets

from backend.app.web.static_files import StaticAsset


class MediaService:
    allowed_types = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }

    def __init__(self, profile_images_dir: Path, max_upload_bytes: int = 4 * 1024 * 1024):
        self.profile_images_dir = profile_images_dir
        self.max_upload_bytes = max_upload_bytes

    def save_profile_image(self, slug: str, filename: str, content_type: str, body: bytes) -> str:
        if not body:
            raise ValueError("Image file is required.")
        if len(body) > self.max_upload_bytes:
            raise ValueError("Image must be 4 MB or smaller.")

        extension = self.extension_for(filename, content_type)
        if not extension:
            raise ValueError("Only JPG, PNG, WEBP, and GIF images are supported.")

        safe_slug = self.safe_segment(slug)
        target_dir = self.profile_images_dir / safe_slug
        target_dir.mkdir(parents=True, exist_ok=True)

        target_name = f"avatar-{secrets.token_hex(8)}{extension}"
        target_path = target_dir / target_name
        target_path.write_bytes(body)
        return f"/media/profile-images/{safe_slug}/{target_name}"

    def load_profile_image(self, slug: str, filename: str) -> Optional[StaticAsset]:
        safe_slug = self.safe_segment(slug)
        safe_filename = self.safe_filename(filename)
        candidate = (self.profile_images_dir / safe_slug / safe_filename).resolve()

        try:
            candidate.relative_to(self.profile_images_dir.resolve())
        except ValueError:
            return None

        if not candidate.is_file():
            return None

        mime_type = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
        return StaticAsset(body=candidate.read_bytes(), mime_type=mime_type)

    def extension_for(self, filename: str, content_type: str) -> str:
        if content_type in self.allowed_types:
            return self.allowed_types[content_type]

        suffix = Path(filename or "").suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            return ".jpg"
        if suffix in {".png", ".webp", ".gif"}:
            return suffix
        return ""

    @staticmethod
    def safe_segment(value: str) -> str:
        return "".join(character for character in value if character.isalnum() or character in "-_") or "profile"

    @staticmethod
    def safe_filename(value: str) -> str:
        return Path(value).name
