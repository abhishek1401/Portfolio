from typing import Any, Dict, Optional
import hashlib
import hmac
import secrets
import time

from backend.app.defaults import DEFAULT_AUTH
from backend.app.domain.dashboard import TEXT_LIMITS, clean_text
from backend.app.storage.json_store import JsonStore


class AuthService:
    def __init__(self, store: JsonStore, session_ttl_seconds: int):
        self.store = store
        self.session_ttl_seconds = session_ttl_seconds
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def ensure_seeded(self) -> None:
        if not self.store.exists():
            self.store.write(DEFAULT_AUTH)

    def login(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self.ensure_seeded()
        credentials = self.store.read(DEFAULT_AUTH)
        username = clean_text(payload.get("username"), TEXT_LIMITS["short"])
        password = str(payload.get("password") or "")

        expected_hash = credentials.get("passwordHash", "")
        actual_hash = self.hash_password(password, credentials.get("passwordSalt", ""))
        if username != credentials.get("username") or not hmac.compare_digest(actual_hash, expected_hash):
            return None

        self.prune_sessions()
        token = secrets.token_urlsafe(32)
        expires_at = int(time.time() + self.session_ttl_seconds)
        self.sessions[token] = {"username": username, "expiresAt": expires_at}
        return {"token": token, "username": username, "expiresAt": expires_at}

    def logout(self, token: str) -> None:
        if token:
            self.sessions.pop(token, None)

    def is_session_valid(self, token: str) -> bool:
        self.prune_sessions()
        return bool(token and token in self.sessions)

    def prune_sessions(self) -> None:
        now = time.time()
        expired = [token for token, details in self.sessions.items() if details["expiresAt"] <= now]
        for token in expired:
            self.sessions.pop(token, None)

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
