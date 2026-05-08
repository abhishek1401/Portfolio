from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List
import re
import shutil
import time

from backend.app.defaults import DEFAULT_DASHBOARD
from backend.app.domain.dashboard import clean_dashboard, clean_text
from backend.app.storage.json_store import JsonStore


class ProfileNotFoundError(ValueError):
    pass


class ProfileService:
    def __init__(self, profiles_dir: Path, index_store: JsonStore, legacy_store: JsonStore, profile_images_dir: Path):
        self.profiles_dir = profiles_dir
        self.index_store = index_store
        self.legacy_store = legacy_store
        self.profile_images_dir = profile_images_dir

    def ensure_seeded(self) -> None:
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.profile_images_dir.mkdir(parents=True, exist_ok=True)

        if self.index_store.exists():
            self._repair_index()
            return

        seed = self.legacy_store.read(DEFAULT_DASHBOARD) if self.legacy_store.exists() else DEFAULT_DASHBOARD
        dashboard = clean_dashboard(seed)
        slug = self.unique_slug(dashboard["user"].get("name") or "profile")
        self.profile_store(slug).write(dashboard)
        self.index_store.write({"defaultSlug": slug, "profiles": [self.summary_from_dashboard(slug, dashboard)]})

    def list_profiles(self) -> Dict[str, Any]:
        self.ensure_seeded()
        index = self.read_index()
        profiles = [self.summary(slug) for slug in self.profile_slugs(index)]
        profiles = [profile for profile in profiles if profile]

        if not profiles:
            self.index_store.path.unlink(missing_ok=True)
            self.ensure_seeded()
            return self.list_profiles()

        default_slug = index.get("defaultSlug")
        if default_slug not in [profile["slug"] for profile in profiles]:
            default_slug = profiles[0]["slug"]
            self.write_index(default_slug, profiles)

        return {"defaultSlug": default_slug, "profiles": profiles}

    def default_slug(self) -> str:
        return str(self.list_profiles()["defaultSlug"])

    def get_profile(self, slug: str) -> Dict[str, Any]:
        slug = self.normalize_slug(slug)
        store = self.profile_store(slug)
        if not store.exists():
            raise ProfileNotFoundError("Profile not found.")
        return clean_dashboard(store.read(DEFAULT_DASHBOARD))

    def get_profile_response(self, slug: str) -> Dict[str, Any]:
        dashboard = self.get_profile(slug)
        return {"profile": self.summary_from_dashboard(slug, dashboard), "dashboard": dashboard}

    def create_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        name = clean_text(payload.get("name"), 120) or "New Profile"
        title = clean_text(payload.get("title"), 120)
        slug = self.unique_slug(payload.get("slug") or name)

        dashboard = deepcopy(DEFAULT_DASHBOARD)
        dashboard["user"]["name"] = name
        dashboard["user"]["title"] = title
        dashboard["user"]["email"] = ""
        dashboard["user"]["phone"] = ""
        dashboard["user"]["location"] = ""
        dashboard["user"]["availability"] = "Available"
        dashboard["user"]["focus"] = ""
        dashboard["user"]["bio"] = ""
        dashboard["projects"] = []
        dashboard["timeline"] = []
        dashboard["links"] = []

        cleaned = clean_dashboard(dashboard)
        self.profile_store(slug).write(cleaned)
        self.upsert_summary(slug, cleaned)
        return self.get_profile_response(slug)

    def save_profile(self, slug: str, payload: Any) -> Dict[str, Any]:
        slug = self.normalize_slug(slug)
        if not self.profile_store(slug).exists():
            raise ProfileNotFoundError("Profile not found.")
        cleaned = clean_dashboard(payload)
        self.profile_store(slug).write(cleaned)
        self.upsert_summary(slug, cleaned)
        return self.get_profile_response(slug)

    def delete_profile(self, slug: str) -> Dict[str, Any]:
        slug = self.normalize_slug(slug)
        listing = self.list_profiles()
        profiles = listing["profiles"]
        if slug not in [profile["slug"] for profile in profiles]:
            raise ProfileNotFoundError("Profile not found.")
        if len(profiles) <= 1:
            raise ValueError("At least one profile is required.")

        self.profile_store(slug).path.unlink(missing_ok=True)
        image_dir = self.profile_images_dir / slug
        if image_dir.exists():
            shutil.rmtree(image_dir)

        remaining = [profile for profile in profiles if profile["slug"] != slug]
        default_slug = listing["defaultSlug"]
        if default_slug == slug:
            default_slug = remaining[0]["slug"]
        self.write_index(default_slug, remaining)
        return {"defaultSlug": default_slug, "profiles": remaining}

    def profile_store(self, slug: str) -> JsonStore:
        return JsonStore(self.profiles_dir / f"{self.normalize_slug(slug)}.json")

    def unique_slug(self, value: Any) -> str:
        base = self.normalize_slug(value)
        candidate = base
        counter = 2
        while self.profile_store(candidate).exists():
            candidate = f"{base}-{counter}"
            counter += 1
        return candidate

    def normalize_slug(self, value: Any) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
        return slug or "profile"

    def read_index(self) -> Dict[str, Any]:
        return self.index_store.read({"defaultSlug": "", "profiles": []})

    def write_index(self, default_slug: str, profiles: List[Dict[str, Any]]) -> None:
        self.index_store.write({"defaultSlug": default_slug, "profiles": profiles})

    def profile_slugs(self, index: Dict[str, Any]) -> List[str]:
        profiles = index.get("profiles", [])
        if not isinstance(profiles, list):
            return []
        return [self.normalize_slug(profile.get("slug")) for profile in profiles if isinstance(profile, dict)]

    def summary(self, slug: str) -> Dict[str, Any]:
        try:
            return self.summary_from_dashboard(slug, self.get_profile(slug))
        except ProfileNotFoundError:
            return {}

    def summary_from_dashboard(self, slug: str, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        user = dashboard["user"]
        path = self.profile_store(slug).path
        updated_at = int(path.stat().st_mtime) if path.exists() else int(time.time())
        return {
            "slug": self.normalize_slug(slug),
            "name": user.get("name", ""),
            "title": user.get("title", ""),
            "avatarUrl": user.get("avatarUrl", ""),
            "publicUrl": f"/profile/{self.normalize_slug(slug)}",
            "updatedAt": updated_at,
        }

    def upsert_summary(self, slug: str, dashboard: Dict[str, Any]) -> None:
        listing = self.list_profiles()
        next_summary = self.summary_from_dashboard(slug, dashboard)
        profiles = [profile for profile in listing["profiles"] if profile["slug"] != slug]
        profiles.append(next_summary)
        profiles.sort(key=lambda profile: profile["name"].lower())
        self.write_index(listing["defaultSlug"] or slug, profiles)

    def _repair_index(self) -> None:
        index = self.read_index()
        slugs = self.profile_slugs(index)
        if slugs:
            return

        profile_files = sorted(self.profiles_dir.glob("*.json"))
        profiles = []
        for profile_file in profile_files:
            if profile_file.name == "index.json":
                continue
            slug = self.normalize_slug(profile_file.stem)
            profiles.append(self.summary(slug))
        profiles = [profile for profile in profiles if profile]
        if profiles:
            self.write_index(profiles[0]["slug"], profiles)
        else:
            self.index_store.path.unlink(missing_ok=True)
            self.ensure_seeded()
