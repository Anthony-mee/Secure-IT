import secrets
from datetime import datetime, timedelta, timezone

from flask import abort, current_app, jsonify, redirect, render_template, request, session, url_for

from secure_it import make_layout
from database import (
    authenticate_user,
    create_pending_user,
    ensure_demo_users,
    get_user_by_email,
    get_user_by_verification_token,
    is_gmail_address,
    update_user_by_email,
    upsert_facebook_user,
    upsert_firebase_user,
)
from cloudinary_uploader import upload_profile_picture
from facebook_auth import (
    build_facebook_login_url,
    exchange_facebook_code,
    fetch_facebook_profile,
    is_facebook_configured,
)
from firebase_auth import get_firebase_web_config, verify_firebase_id_token
from mailer import send_verification_email


def _start_session(user: dict):
    session["logged_in"] = True
    session["user_role"] = str(user.get("role", "student")).strip().lower()
    session["user_email"] = user.get("email")
    session["display_name"] = user.get("name")
    session["year_level"] = user.get("year_level", "")
    session["profile_picture"] = user.get("profile_picture", "")
    session["email_verified"] = bool(user.get("email_verified", False))


def _verification_required() -> bool:
    return bool(current_app.config.get("REQUIRE_EMAIL_VERIFICATION", True))


def login_page():
    message = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        ensure_demo_users()
        user = authenticate_user(email, password)
        if user:
            _start_session(user)
            return redirect(url_for("dashboard_page"))

        existing_user = get_user_by_email(email)
        if existing_user and not existing_user.get("email_verified", False):
            message = "Please verify your email before logging in."
        else:
            message = "Invalid email or password."

    return make_layout(
        "login",
        "Secure-IT Login",
        "Access the cybersecurity training dashboard",
        "login.html",
        message=message,
        firebase_config=get_firebase_web_config(),
        facebook_enabled=is_facebook_configured(),
    )


def register_page():
    if request.method != "POST":
        return redirect(url_for("login_page"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    year_level = request.form.get("year_level", "").strip()
    profile_picture = request.files.get("profile_picture")

    if not name or not email or not password:
        return redirect(url_for("login_page", register_error="Please fill in all fields.", register_open=1))

    if not is_gmail_address(email):
        return redirect(url_for("login_page", register_error="Use a real Gmail address for registration.", register_open=1))

    if password != confirm_password:
        return redirect(url_for("login_page", register_error="Passwords do not match.", register_open=1))

    if not year_level:
        return redirect(url_for("login_page", register_error="Select your year level.", register_open=1))

    profile_picture_path = ""
    if profile_picture and profile_picture.filename:
        if not getattr(profile_picture, "mimetype", "").startswith("image/"):
            return redirect(url_for("login_page", register_error="Profile picture must be a JPG, PNG, or WEBP image.", register_open=1))

        uploaded_image = upload_profile_picture(profile_picture)
        if uploaded_image is None:
            return redirect(url_for("login_page", register_error="Could not upload profile picture right now.", register_open=1))

        profile_picture_path = uploaded_image

    ensure_demo_users()
    if get_user_by_email(email):
        return redirect(url_for("login_page", register_error="That email is already registered.", register_open=1))

    token = secrets.token_urlsafe(32)
    expires_hours = int(current_app.config.get("EMAIL_VERIFY_TTL_HOURS", 24))
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    user = create_pending_user(
        name=name,
        email=email,
        password=password,
        year_level=year_level,
        profile_picture=profile_picture_path,
        verification_token=token,
        verification_expires_at=expires_at,
        email_verified=not _verification_required(),
    )
    if not user:
        return redirect(url_for("login_page", register_error="Could not create account.", register_open=1))

    update_user_by_email(
        email,
        {
            "year_level": year_level,
            "profile_picture": profile_picture_path,
            "verification_token": token,
            "verification_expires_at": expires_at,
            "email_verified": not _verification_required(),
        },
    )

    verification_url = url_for("verify_email_page", token=token, _external=True)
    send_verification_email(email, verification_url, year_level, profile_picture_path)

    if _verification_required():
        return redirect(url_for("login_page", register_error="Check your email to verify your account.", register_open=1))

    user = authenticate_user(email, password)
    if user:
        _start_session(user)
        return redirect(url_for("dashboard_page"))

    return redirect(url_for("login_page", register_error="Could not create account.", register_open=1))


def verify_email_page(token: str):
    user = get_user_by_verification_token(token)
    if not user:
        return render_template("social_popup.html", provider="Email", success=False)

    expires_at = user.get("verification_expires_at")
    if expires_at and getattr(expires_at, "tzinfo", None) is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at and expires_at < datetime.now(timezone.utc):
        return render_template("social_popup.html", provider="Email", success=False)

    update_user_by_email(
        user["email"],
        {
            "email_verified": True,
            "verification_token": "",
            "verification_expires_at": None,
        },
    )
    _start_session({**user, "email_verified": True})
    return redirect(url_for("dashboard_page"))


def social_login_page(provider: str):
    abort(404)


def facebook_login_page():
    if not is_facebook_configured():
        return redirect(url_for("login_page", register_error="Facebook login is not configured yet."))

    state = secrets.token_urlsafe(32)
    session["facebook_oauth_state"] = state
    redirect_uri = url_for("facebook_callback_page", _external=True)
    return redirect(build_facebook_login_url(state=state, redirect_uri=redirect_uri))


def facebook_callback_page():
    if not is_facebook_configured():
        return redirect(url_for("login_page", register_error="Facebook login is not configured yet."))

    error = request.args.get("error")
    if error:
        return redirect(url_for("login_page", register_error="Facebook sign-in was cancelled."))

    state = request.args.get("state", "")
    code = request.args.get("code", "")
    expected_state = session.pop("facebook_oauth_state", "")
    if not code or not state or state != expected_state:
        return redirect(url_for("login_page", register_error="Facebook sign-in failed. Please try again."))

    redirect_uri = url_for("facebook_callback_page", _external=True)
    access_token = exchange_facebook_code(code=code, redirect_uri=redirect_uri)
    if not access_token:
        return redirect(url_for("login_page", register_error="Could not verify Facebook login."))

    profile = fetch_facebook_profile(access_token)
    if not profile:
        return redirect(url_for("login_page", register_error="Could not load your Facebook profile."))

    user = upsert_facebook_user(
        facebook_id=profile["facebook_id"],
        email=profile["email"],
        name=profile["name"],
        profile_picture=profile["profile_picture"],
    )
    if not user:
        return redirect(url_for("login_page", register_error="Could not sign in with Facebook right now."))

    _start_session(user)
    return redirect(url_for("dashboard_page"))


def firebase_login():
    if request.method != "POST":
        abort(405)

    payload = request.get_json(silent=True) or {}
    id_token = str(payload.get("idToken", "")).strip()
    if not id_token:
        return jsonify({"error": "Missing Firebase token."}), 400

    decoded_token = verify_firebase_id_token(id_token)
    if not decoded_token:
        return jsonify({"error": "Invalid or expired Firebase token."}), 401

    email = str(decoded_token.get("email", "")).strip().lower()
    if not email:
        return jsonify({"error": "Google account email is not available."}), 400

    if not decoded_token.get("email_verified", False):
        return jsonify({"error": "Google email is not verified."}), 403

    name = str(decoded_token.get("name") or email.split("@")[0]).strip()
    user = upsert_firebase_user(
        email=email,
        name=name,
        profile_picture=str(decoded_token.get("picture", "")).strip(),
        firebase_uid=str(decoded_token.get("uid", "")).strip(),
        provider="google",
    )
    if not user:
        return jsonify({"error": "Could not sign in with Google right now."}), 500

    _start_session(user)
    return jsonify({"success": True, "redirect": url_for("dashboard_page")})


def logout_page():
    session.pop("logged_in", None)
    session.pop("user_role", None)
    session.pop("user_email", None)
    session.pop("display_name", None)
    session.pop("year_level", None)
    session.pop("profile_picture", None)
    session.pop("email_verified", None)
    return redirect(url_for("landing_page"))
