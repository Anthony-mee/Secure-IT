import os
from pathlib import Path
from urllib.parse import urlencode

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during setup
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent
GRAPH_API_VERSION = "v21.0"
FACEBOOK_OAUTH_URL = f"https://www.facebook.com/{GRAPH_API_VERSION}/dialog/oauth"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")


def is_facebook_configured() -> bool:
    return bool(os.getenv("FACEBOOK_APP_ID", "").strip() and os.getenv("FACEBOOK_APP_SECRET", "").strip())


def build_facebook_login_url(*, state: str, redirect_uri: str) -> str:
    params = {
        "client_id": os.getenv("FACEBOOK_APP_ID", "").strip(),
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": "email,public_profile",
        "response_type": "code",
    }
    return f"{FACEBOOK_OAUTH_URL}?{urlencode(params)}"


def exchange_facebook_code(*, code: str, redirect_uri: str) -> str | None:
    params = {
        "client_id": os.getenv("FACEBOOK_APP_ID", "").strip(),
        "client_secret": os.getenv("FACEBOOK_APP_SECRET", "").strip(),
        "redirect_uri": redirect_uri,
        "code": code,
    }

    try:
        response = requests.get(f"{FACEBOOK_GRAPH_URL}/oauth/access_token", params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return None

    access_token = payload.get("access_token")
    return str(access_token).strip() if access_token else None


def fetch_facebook_profile(access_token: str) -> dict | None:
    params = {
        "fields": "id,name,email,picture.type(large)",
        "access_token": access_token,
    }

    try:
        response = requests.get(f"{FACEBOOK_GRAPH_URL}/me", params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return None

    facebook_id = str(payload.get("id", "")).strip()
    if not facebook_id:
        return None

    picture_data = payload.get("picture", {})
    if isinstance(picture_data, dict):
        picture_url = str(picture_data.get("data", {}).get("url", "")).strip()
    else:
        picture_url = ""

    return {
        "facebook_id": facebook_id,
        "name": str(payload.get("name") or f"Facebook User {facebook_id}").strip(),
        "email": str(payload.get("email", "")).strip().lower(),
        "profile_picture": picture_url,
    }
