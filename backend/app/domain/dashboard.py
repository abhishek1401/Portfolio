from typing import Any, Callable, Dict, List, Optional


TEXT_LIMITS = {
    "short": 120,
    "medium": 320,
    "long": 1200,
    "url": 600,
}


def clean_text(value: Any, limit: int) -> str:
    if value is None:
        return ""
    return str(value).strip()[:limit]


def clean_url(value: Any) -> str:
    return clean_text(value, TEXT_LIMITS["url"])


def clean_list(values: Any, max_items: int, cleaner: Callable[[Any], Optional[Any]]) -> List[Any]:
    if not isinstance(values, list):
        return []

    cleaned = []
    for value in values[:max_items]:
        item = cleaner(value)
        if item:
            cleaned.append(item)
    return cleaned


def clean_dashboard(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Dashboard payload must be an object.")

    incoming_user = payload.get("user", {})
    if not isinstance(incoming_user, dict):
        incoming_user = {}

    user = {
        "name": clean_text(incoming_user.get("name"), TEXT_LIMITS["short"]),
        "title": clean_text(incoming_user.get("title"), TEXT_LIMITS["short"]),
        "location": clean_text(incoming_user.get("location"), TEXT_LIMITS["short"]),
        "email": clean_text(incoming_user.get("email"), TEXT_LIMITS["short"]),
        "phone": clean_text(incoming_user.get("phone"), TEXT_LIMITS["short"]),
        "availability": clean_text(incoming_user.get("availability"), TEXT_LIMITS["medium"]),
        "focus": clean_text(incoming_user.get("focus"), TEXT_LIMITS["medium"]),
        "bio": clean_text(incoming_user.get("bio"), TEXT_LIMITS["long"]),
        "avatarUrl": clean_url(incoming_user.get("avatarUrl")),
        "themeColor": clean_text(incoming_user.get("themeColor") or "#176b87", 24),
    }

    if not user["avatarUrl"]:
        user["avatarUrl"] = "/assets/default-avatar.svg"
    if not user["name"]:
        user["name"] = "Unnamed User"

    return {
        "user": user,
        "stats": clean_list(payload.get("stats"), 8, clean_stat),
        "skills": clean_list(payload.get("skills"), 24, clean_skill),
        "projects": clean_list(payload.get("projects"), 12, clean_project),
        "timeline": clean_list(payload.get("timeline"), 12, clean_timeline_item),
        "links": clean_list(payload.get("links"), 12, clean_link),
    }


def clean_stat(item: Any) -> Optional[Dict[str, str]]:
    if not isinstance(item, dict):
        return None
    return {
        "label": clean_text(item.get("label"), TEXT_LIMITS["short"]),
        "value": clean_text(item.get("value"), TEXT_LIMITS["short"]),
        "detail": clean_text(item.get("detail"), TEXT_LIMITS["medium"]),
    }


def clean_skill(item: Any) -> str:
    return clean_text(item, TEXT_LIMITS["short"])


def clean_project(item: Any) -> Optional[Dict[str, str]]:
    if not isinstance(item, dict):
        return None
    return {
        "name": clean_text(item.get("name"), TEXT_LIMITS["short"]),
        "description": clean_text(item.get("description"), TEXT_LIMITS["long"]),
        "status": clean_text(item.get("status"), TEXT_LIMITS["short"]),
        "link": clean_url(item.get("link")),
    }


def clean_timeline_item(item: Any) -> Optional[Dict[str, str]]:
    if not isinstance(item, dict):
        return None
    return {
        "date": clean_text(item.get("date"), TEXT_LIMITS["short"]),
        "title": clean_text(item.get("title"), TEXT_LIMITS["short"]),
        "description": clean_text(item.get("description"), TEXT_LIMITS["long"]),
    }


def clean_link(item: Any) -> Optional[Dict[str, str]]:
    if not isinstance(item, dict):
        return None
    return {
        "label": clean_text(item.get("label"), TEXT_LIMITS["short"]),
        "url": clean_url(item.get("url")),
    }
