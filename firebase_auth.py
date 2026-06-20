import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during setup
    load_dotenv = None

try:
    import firebase_admin
    from firebase_admin import auth, credentials
except ImportError:  # pragma: no cover - optional during setup
    firebase_admin = None
    auth = None
    credentials = None

BASE_DIR = Path(__file__).resolve().parent
_initialized = False

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")


def _credentials_path() -> Path | None:
    raw_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "").strip()
    if not raw_path:
        return None

    path = Path(raw_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path if path.is_file() else None


def get_firebase_web_config() -> dict | None:
    config = {
        "apiKey": os.getenv("FIREBASE_API_KEY", "").strip(),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "").strip(),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", "").strip(),
        "appId": os.getenv("FIREBASE_APP_ID", "").strip(),
    }
    if not all(config.values()):
        return None
    return config


def init_firebase() -> bool:
    global _initialized
    if _initialized:
        return True
    if firebase_admin is None or credentials is None:
        return False

    credential_path = _credentials_path()
    if credential_path is None:
        return False

    try:
        firebase_admin.initialize_app(credentials.Certificate(str(credential_path)))
    except ValueError:
        # App already initialized in this process.
        pass
    except Exception:
        return False

    _initialized = True
    return True


def verify_firebase_id_token(id_token: str) -> dict | None:
    if not id_token or auth is None or not init_firebase():
        return None

    try:
        return auth.verify_id_token(id_token)
    except Exception:
        return None
