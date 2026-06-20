from dataclasses import dataclass
from datetime import datetime, timezone
import os
import secrets
from pathlib import Path
from functools import lru_cache
from typing import Any

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:  # pragma: no cover - dependency may not be installed yet
    MongoClient = None

    class PyMongoError(Exception):
        pass

from werkzeug.security import check_password_hash, generate_password_hash


@dataclass(frozen=True)
class StudentProfile:
    name: str
    level: str
    points: int
    badges: list[str]
    completion: int
    year_level: str = ""
    profile_picture: str = ""


DEFAULT_PROFILE = StudentProfile(
    name="You",
    level="Beginner",
    points=860,
    badges=["Starter Shield", "Phish Hunter", "Password Guardian"],
    completion=68,
)

DEFAULT_METRICS = {
    "modules_complete": 4,
    "total_modules": 6,
    "average_score": 78,
    "active_simulations": 5,
}

DEFAULT_ATTEMPTS = [
    "/admin/login",
    "/wp-admin",
    "/api/v1/users",
    "/admin/dashboard",
    "/backup.zip",
    "/hidden-panel",
    "/.git/config",
    "/portal/settings",
]

DEFAULT_DEMO_USERS = [
    {
        "name": "Demo Student",
        "email": "student@secure-it.local",
        "password": "student123",
        "role": "student",
    },
    {
        "name": "Demo Admin",
        "email": "admin@secure-it.local",
        "password": "admin123",
        "role": "admin",
    },
]

UPLOAD_DIRECTORY = Path(__file__).resolve().parent / "static" / "uploads" / "profiles"


def _default_database_name() -> str:
    return os.getenv("DB_NAME") or os.getenv("MONGO_DB_NAME") or "secure_it"


@lru_cache(maxsize=1)
def get_mongo_client():
    db_uri = os.getenv("DB_URI") or os.getenv("MONGODB_URI")
    if not db_uri or MongoClient is None:
        return None

    try:
        return MongoClient(db_uri, serverSelectionTimeoutMS=2500)
    except PyMongoError:
        return None


def get_database():
    client = get_mongo_client()
    if client is None:
        return None

    try:
        client.admin.command("ping")
    except PyMongoError:
        return None

    return client[_default_database_name()]


def _collection(name: str):
    database = get_database()
    if database is None:
        return None
    return database[name]


def _users_collection():
    collection = _collection("users")
    if collection is None:
        return None

    try:
        collection.create_index("email", unique=True)
    except PyMongoError:
        pass

    return collection


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _is_gmail_address(email: str) -> bool:
    normalized_email = _normalize_email(email)
    return normalized_email.endswith("@gmail.com") or normalized_email.endswith("@googlemail.com")


def _utcnow():
    return datetime.now(timezone.utc)


def _to_profile(document: dict | None) -> StudentProfile:
    if not document:
        return DEFAULT_PROFILE

    return StudentProfile(
        name=str(document.get("name", DEFAULT_PROFILE.name)),
        level=str(document.get("level", DEFAULT_PROFILE.level)),
        points=int(document.get("points", DEFAULT_PROFILE.points)),
        badges=list(document.get("badges", DEFAULT_PROFILE.badges)),
        completion=int(document.get("completion", DEFAULT_PROFILE.completion)),
        year_level=str(document.get("year_level", "")),
        profile_picture=str(document.get("profile_picture", "")),
    )


def get_student_profile() -> StudentProfile:
    collection = _collection("profiles")
    if collection is None:
        return DEFAULT_PROFILE

    document = collection.find_one({}, sort=[("updated_at", -1), ("_id", -1)])
    return _to_profile(document)


def get_metrics() -> dict:
    collection = _collection("metrics")
    if collection is None:
        return DEFAULT_METRICS.copy()

    document = collection.find_one({}, sort=[("updated_at", -1), ("_id", -1)])
    if not document:
        return DEFAULT_METRICS.copy()

    metrics = DEFAULT_METRICS.copy()
    metrics.update({
        "modules_complete": int(document.get("modules_complete", metrics["modules_complete"])),
        "total_modules": int(document.get("total_modules", metrics["total_modules"])),
        "average_score": int(document.get("average_score", metrics["average_score"])),
        "active_simulations": int(document.get("active_simulations", metrics["active_simulations"])),
    })
    return metrics


def get_recent_attempts() -> list[str]:
    collection = _collection("attempts")
    if collection is None:
        return DEFAULT_ATTEMPTS.copy()

    attempts: list[str] = []
    for document in collection.find({}, sort=[("created_at", -1), ("_id", -1)]).limit(20):
        attempt = document.get("path") or document.get("attempt") or document.get("value")
        if attempt:
            attempts.append(str(attempt))

    return attempts or DEFAULT_ATTEMPTS.copy()


def get_user_by_email(email: str):
    collection = _users_collection()
    if collection is None:
        return None

    return collection.find_one({"email": _normalize_email(email)})


def list_all_users() -> list[dict]:
    collection = _users_collection()
    if collection is None:
        return []

    return list(collection.find({}, sort=[("updated_at", -1)]))


def log_activity(email: str, activity_type: str, details: dict[str, Any] | None = None):
    db = get_database()
    if db is None:
        return

    try:
        db["activity_logs"].insert_one(
            {
                "email": _normalize_email(email),
                "activity_type": activity_type,
                "details": details or {},
                "created_at": _utcnow(),
            }
        )
    except PyMongoError:
        pass


def get_user_simulation_history(email: str, limit: int = 10) -> list[dict]:
    collection = _simulation_results_collection()
    if collection is None:
        return []

    return list(
        collection.find({"email": _normalize_email(email)}, sort=[("completed_at", -1)]).limit(limit)
    )


def get_user_dashboard_data(email: str) -> dict[str, Any]:
    user = get_user_by_email(email)
    history = get_user_simulation_history(email, limit=8)
    progress = get_user_progress(email)
    metrics = get_metrics()

    badges = list(DEFAULT_PROFILE.badges)
    if progress["points"] >= 500:
        badges.append("Mission Operator")
    if progress["points"] >= 1500:
        badges.append("Threat Hunter")
    if len(progress["simulations_completed"]) >= 3:
        badges.append("Range Explorer")

    sim_scores = [int(h.get("simulation_score", 0)) for h in history if h.get("simulation_score") is not None]
    quiz_scores = [int(h.get("quiz_score", 0)) for h in history if h.get("quiz_score") is not None]
    all_scores = sim_scores + quiz_scores
    average_score = round(sum(all_scores) / len(all_scores)) if all_scores else metrics.get("average_score", 0)

    completion = round((len(progress["simulations_completed"]) / max(len(list_attack_ids()), 1)) * 100)

    return {
        "name": user.get("name", "Student") if user else "Student",
        "points": progress["points"],
        "level": progress["level"],
        "completion": min(completion, 100),
        "badges": badges,
        "simulations_completed": progress["simulations_completed"],
        "history": history,
        "average_score": average_score,
        "metrics": metrics,
    }


def list_attack_ids() -> list[str]:
    try:
        from simulation_data import ATTACKS

        return list(ATTACKS.keys())
    except ImportError:
        return []


def get_user_by_verification_token(token: str):
    collection = _users_collection()
    if collection is None:
        return None

    return collection.find_one({"verification_token": token})


def update_user_by_email(email: str, updates: dict[str, Any]):
    collection = _users_collection()
    if collection is None:
        return None

    normalized_email = _normalize_email(email)
    document_updates = dict(updates)
    document_updates["updated_at"] = _utcnow()

    try:
        collection.update_one({"email": normalized_email}, {"$set": document_updates})
    except PyMongoError:
        return None

    return collection.find_one({"email": normalized_email})


def create_pending_user(
    name: str,
    email: str,
    password: str,
    role: str = "student",
    year_level: str = "",
    profile_picture: str = "",
    verification_token: str = "",
    verification_expires_at=None,
    email_verified: bool = False,
):
    collection = _users_collection()
    if collection is None:
        return None

    document = {
        "name": name.strip(),
        "email": _normalize_email(email),
        "password_hash": generate_password_hash(password),
        "role": role,
        "provider": "local",
        "year_level": year_level.strip(),
        "profile_picture": profile_picture,
        "email_verified": email_verified,
        "verification_token": verification_token,
        "verification_expires_at": verification_expires_at,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
    }

    try:
        collection.insert_one(document)
    except PyMongoError:
        return None

    return document


def create_user(name: str, email: str, password: str, role: str = "student"):
    return create_pending_user(name=name, email=email, password=password, role=role)


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None

    if not user.get("email_verified", False) and str(os.getenv("REQUIRE_EMAIL_VERIFICATION", "true")).lower() == "true":
        return None

    password_hash = user.get("password_hash")
    if not password_hash or not check_password_hash(password_hash, password):
        return None

    return user


def ensure_demo_users():
    collection = _users_collection()
    if collection is None:
        return

    for demo_user in DEFAULT_DEMO_USERS:
        if collection.find_one({"email": demo_user["email"]}):
            continue

        try:
            collection.insert_one(
                {
                    "name": demo_user["name"],
                    "email": demo_user["email"],
                    "password_hash": generate_password_hash(demo_user["password"]),
                    "role": demo_user["role"],
                    "provider": "local",
                    "email_verified": True,
                    "created_at": _utcnow(),
                    "updated_at": _utcnow(),
                }
            )
        except PyMongoError:
            continue


def upsert_firebase_user(
    *,
    email: str,
    name: str,
    profile_picture: str = "",
    firebase_uid: str = "",
    provider: str = "google",
):
    collection = _users_collection()
    if collection is None:
        return None

    normalized_email = _normalize_email(email)
    existing_user = collection.find_one({"email": normalized_email})
    updates = {
        "name": name.strip(),
        "provider": provider.strip().lower(),
        "email_verified": True,
        "firebase_uid": firebase_uid,
        "updated_at": _utcnow(),
    }
    if profile_picture:
        updates["profile_picture"] = profile_picture

    if existing_user:
        try:
            collection.update_one({"email": normalized_email}, {"$set": updates})
        except PyMongoError:
            return None
        return collection.find_one({"email": normalized_email})

    document = {
        "name": name.strip(),
        "email": normalized_email,
        "password_hash": generate_password_hash(secrets.token_urlsafe(32)),
        "role": "student",
        "provider": provider.strip().lower(),
        "year_level": "",
        "profile_picture": profile_picture,
        "email_verified": True,
        "firebase_uid": firebase_uid,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
    }

    try:
        collection.insert_one(document)
    except PyMongoError:
        return None

    return document


def is_gmail_address(email: str) -> bool:
    return _is_gmail_address(email)


def ensure_upload_directory() -> Path:
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIRECTORY


def _simulation_results_collection():
    collection = _collection("simulation_results")
    if collection is None:
        return None
    try:
        collection.create_index([("email", 1), ("attack_id", 1), ("completed_at", -1)])
    except PyMongoError:
        pass
    return collection


def _level_for_points(points: int) -> str:
    if points >= 2500:
        return "Advanced"
    if points >= 1000:
        return "Intermediate"
    return "Beginner"


def record_simulation_completion(
    email: str,
    attack_id: str,
    *,
    simulation_score: int,
    quiz_score: int | None = None,
    points_earned: int = 0,
    mistakes: list | None = None,
    good_actions: list | None = None,
    time_spent_seconds: int = 0,
    actions_log: list | None = None,
    skills_developed: list | None = None,
):
    collection = _users_collection()
    results = _simulation_results_collection()
    if collection is None:
        return None

    normalized_email = _normalize_email(email)
    user = collection.find_one({"email": normalized_email})
    if not user:
        return None

    current_points = int(user.get("points", 0))
    new_points = current_points + max(points_earned, 0)
    completed = list(user.get("simulations_completed", []))
    if attack_id not in completed:
        completed.append(attack_id)

    updates = {
        "points": new_points,
        "level": _level_for_points(new_points),
        "simulations_completed": completed,
        "updated_at": _utcnow(),
    }

    try:
        collection.update_one({"email": normalized_email}, {"$set": updates})
    except PyMongoError:
        return None

    result_doc = {
        "email": normalized_email,
        "attack_id": attack_id,
        "simulation_score": simulation_score,
        "quiz_score": quiz_score,
        "points_earned": points_earned,
        "mistakes": mistakes or [],
        "good_actions": good_actions or [],
        "time_spent_seconds": time_spent_seconds,
        "actions_log": actions_log or [],
        "skills_developed": skills_developed or [],
        "completed_at": _utcnow(),
    }

    if results is not None:
        try:
            results.insert_one(result_doc)
        except PyMongoError:
            pass

    log_activity(
        normalized_email,
        "simulation_completed",
        {
            "attack_id": attack_id,
            "simulation_score": simulation_score,
            "quiz_score": quiz_score,
            "mistakes": mistakes or [],
        },
    )

    return collection.find_one({"email": normalized_email})


def get_user_progress(email: str) -> dict[str, Any]:
    user = get_user_by_email(email)
    if not user:
        return {"points": 0, "level": "Beginner", "simulations_completed": []}

    return {
        "points": int(user.get("points", 0)),
        "level": str(user.get("level", _level_for_points(int(user.get("points", 0))))),
        "simulations_completed": list(user.get("simulations_completed", [])),
    }
