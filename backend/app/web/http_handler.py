from http.server import BaseHTTPRequestHandler
from typing import Any, Dict
from urllib.parse import unquote, urlparse
import cgi
import json

from backend.app.config import Settings
from backend.app.services.auth_service import AuthService
from backend.app.services.media_service import MediaService
from backend.app.services.profile_service import ProfileNotFoundError, ProfileService
from backend.app.web.static_files import StaticFileService


def build_request_handler(
    settings: Settings,
    profile_service: ProfileService,
    auth_service: AuthService,
    media_service: MediaService,
    static_files: StaticFileService,
):
    class DashboardRequestHandler(BaseHTTPRequestHandler):
        server_version = "UserDashboardHTTP/2.0"

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            self.send_cors_headers()
            self.end_headers()

        def do_GET(self) -> None:
            path = urlparse(self.path).path

            if path == "/api/health":
                self.send_json({"status": "ok", "storage": str(settings.profiles_dir.relative_to(settings.base_dir))})
                return

            if path == "/api/public":
                self.send_json(profile_service.get_profile(profile_service.default_slug()))
                return

            public_slug = self.slug_from_path(path, "/api/public/profiles/")
            if public_slug:
                try:
                    self.send_json(profile_service.get_profile_response(public_slug))
                except ProfileNotFoundError as error:
                    self.send_error_json(404, str(error))
                return

            media_parts = self.media_parts(path)
            if media_parts:
                self.serve_media(media_parts["slug"], media_parts["filename"])
                return

            if path == "/api/admin/dashboard":
                if not self.require_admin():
                    return
                self.send_json(profile_service.get_profile(profile_service.default_slug()))
                return

            if path == "/api/admin/profiles":
                if not self.require_admin():
                    return
                self.send_json(profile_service.list_profiles())
                return

            admin_slug = self.slug_from_path(path, "/api/admin/profiles/")
            if admin_slug:
                if not self.require_admin():
                    return
                try:
                    self.send_json(profile_service.get_profile_response(admin_slug))
                except ProfileNotFoundError as error:
                    self.send_error_json(404, str(error))
                return

            self.serve_static(path)

        def do_POST(self) -> None:
            path = urlparse(self.path).path

            if path == "/api/admin/login":
                self.handle_login()
                return

            if path == "/api/admin/logout":
                auth_service.logout(self.bearer_token())
                self.send_json({"status": "signed_out"})
                return

            if path == "/api/admin/profiles":
                if not self.require_admin():
                    return
                try:
                    self.send_json(profile_service.create_profile(self.read_json_body()), status=201)
                except ValueError as error:
                    self.send_error_json(400, str(error))
                return

            image_slug = self.image_upload_slug(path)
            if image_slug:
                if not self.require_admin():
                    return
                self.handle_image_upload(image_slug)
                return

            self.send_error_json(404, "Route not found.")

        def do_PUT(self) -> None:
            path = urlparse(self.path).path

            if path == "/api/admin/dashboard":
                if not self.require_admin():
                    return
                try:
                    saved = profile_service.save_profile(profile_service.default_slug(), self.read_json_body())
                except ValueError as error:
                    self.send_error_json(400, str(error))
                    return
                self.send_json(saved["dashboard"] if "dashboard" in saved else saved)
                return

            admin_slug = self.slug_from_path(path, "/api/admin/profiles/")
            if admin_slug:
                if not self.require_admin():
                    return
                try:
                    self.send_json(profile_service.save_profile(admin_slug, self.read_json_body()))
                except ProfileNotFoundError as error:
                    self.send_error_json(404, str(error))
                except ValueError as error:
                    self.send_error_json(400, str(error))
                return

            self.send_error_json(404, "Route not found.")

        def do_DELETE(self) -> None:
            path = urlparse(self.path).path
            admin_slug = self.slug_from_path(path, "/api/admin/profiles/")
            if admin_slug:
                if not self.require_admin():
                    return
                try:
                    self.send_json(profile_service.delete_profile(admin_slug))
                except ProfileNotFoundError as error:
                    self.send_error_json(404, str(error))
                except ValueError as error:
                    self.send_error_json(400, str(error))
                return

            self.send_error_json(404, "Route not found.")

        def handle_login(self) -> None:
            try:
                payload = self.read_json_body()
            except ValueError as error:
                self.send_error_json(400, str(error))
                return

            session = auth_service.login(payload)
            if not session:
                self.send_error_json(401, "Invalid admin credentials.")
                return

            self.send_json(session)

        def require_admin(self) -> bool:
            if not auth_service.is_session_valid(self.bearer_token()):
                self.send_error_json(401, "Admin access required.")
                return False
            return True

        def bearer_token(self) -> str:
            auth_header = self.headers.get("Authorization", "")
            prefix = "Bearer "
            if auth_header.startswith(prefix):
                return auth_header[len(prefix):].strip()
            return ""

        def read_json_body(self) -> Dict[str, Any]:
            length_header = self.headers.get("Content-Length")
            try:
                length = int(length_header or "0")
            except ValueError as error:
                raise ValueError("Invalid content length.") from error

            if length <= 0:
                return {}

            raw_body = self.rfile.read(length)
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError as error:
                raise ValueError("Invalid JSON body.") from error

            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object.")
            return payload

        def handle_image_upload(self, slug: str) -> None:
            content_type = self.headers.get("Content-Type", "")
            if not content_type.startswith("multipart/form-data"):
                self.send_error_json(400, "Image upload must use multipart/form-data.")
                return

            try:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        "REQUEST_METHOD": "POST",
                        "CONTENT_TYPE": content_type,
                        "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
                    },
                )
                file_item = form["image"] if "image" in form else None
                if file_item is None or not getattr(file_item, "filename", ""):
                    raise ValueError("Image file is required.")

                body = file_item.file.read(media_service.max_upload_bytes + 1)
                avatar_url = media_service.save_profile_image(
                    slug=slug,
                    filename=file_item.filename,
                    content_type=getattr(file_item, "type", "") or "",
                    body=body,
                )
            except ValueError as error:
                self.send_error_json(400, str(error))
                return

            self.send_json({"avatarUrl": avatar_url})

        def slug_from_path(self, path: str, prefix: str) -> str:
            if path.startswith(prefix) and len(path) > len(prefix):
                remainder = path[len(prefix):].strip("/")
                if "/" not in remainder:
                    return unquote(remainder)
            return ""

        def image_upload_slug(self, path: str) -> str:
            prefix = "/api/admin/profiles/"
            suffix = "/image"
            if path.startswith(prefix) and path.endswith(suffix):
                slug = path[len(prefix):-len(suffix)].strip("/")
                if slug and "/" not in slug:
                    return unquote(slug)
            return ""

        def media_parts(self, path: str) -> Dict[str, str]:
            prefix = "/media/profile-images/"
            if not path.startswith(prefix):
                return {}
            remainder = path[len(prefix):].strip("/")
            parts = remainder.split("/", 1)
            if len(parts) != 2:
                return {}
            return {"slug": unquote(parts[0]), "filename": unquote(parts[1])}

        def serve_media(self, slug: str, filename: str) -> None:
            asset = media_service.load_profile_image(slug, filename)
            if not asset:
                self.send_error_json(404, "Image not found.")
                return

            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", asset.mime_type)
            self.send_header("Content-Length", str(len(asset.body)))
            self.end_headers()
            self.wfile.write(asset.body)

        def serve_static(self, path: str) -> None:
            asset = static_files.load(path)
            if not asset:
                self.send_error_json(404, "Static file not found. Run the frontend build if dist is missing.")
                return

            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", asset.mime_type)
            self.send_header("Content-Length", str(len(asset.body)))
            self.end_headers()
            self.wfile.write(asset.body)

        def send_json(self, payload: Any, status: int = 200) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_error_json(self, status: int, message: str) -> None:
            self.send_json({"error": message}, status=status)

        def send_cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

        def log_message(self, format_string: str, *args: Any) -> None:
            print("%s - %s" % (self.address_string(), format_string % args))

    return DashboardRequestHandler
