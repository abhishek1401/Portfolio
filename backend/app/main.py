from http.server import ThreadingHTTPServer

from backend.app.config import Settings, get_settings
from backend.app.services.auth_service import AuthService
from backend.app.services.media_service import MediaService
from backend.app.services.profile_service import ProfileService
from backend.app.storage.json_store import JsonStore
from backend.app.web.http_handler import build_request_handler
from backend.app.web.static_files import StaticFileService


def create_server(settings: Settings = None) -> ThreadingHTTPServer:
    settings = settings or get_settings()
    profile_service = ProfileService(
        profiles_dir=settings.profiles_dir,
        index_store=JsonStore(settings.profiles_index_file),
        legacy_store=JsonStore(settings.dashboard_file),
        profile_images_dir=settings.profile_images_dir,
    )
    auth_service = AuthService(JsonStore(settings.auth_file), settings.session_ttl_seconds)
    media_service = MediaService(settings.profile_images_dir)

    profile_service.ensure_seeded()
    auth_service.ensure_seeded()

    handler = build_request_handler(
        settings=settings,
        profile_service=profile_service,
        auth_service=auth_service,
        media_service=media_service,
        static_files=StaticFileService(settings.frontend_dist_dir),
    )
    return ThreadingHTTPServer((settings.host, settings.port), handler)


def run() -> None:
    settings = get_settings()
    server = create_server(settings)
    print(f"User dashboard running at http://{settings.host}:{settings.port}")
    print("Admin login: admin / admin123")
    server.serve_forever()
