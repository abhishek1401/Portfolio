from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    cfg_dir: Path
    dashboard_file: Path
    auth_file: Path
    profiles_dir: Path
    profiles_index_file: Path
    profile_images_dir: Path
    frontend_dist_dir: Path
    host: str
    port: int
    session_ttl_seconds: int


def get_settings() -> Settings:
    base_dir = Path(__file__).resolve().parents[2]
    cfg_dir = base_dir / "cfg"
    return Settings(
        base_dir=base_dir,
        cfg_dir=cfg_dir,
        dashboard_file=cfg_dir / "user_dashboard.json",
        auth_file=cfg_dir / "auth.json",
        profiles_dir=cfg_dir / "profiles",
        profiles_index_file=cfg_dir / "profiles" / "index.json",
        profile_images_dir=cfg_dir / "profile_images",
        frontend_dist_dir=base_dir / "frontend" / "dist",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        session_ttl_seconds=8 * 60 * 60,
    )
