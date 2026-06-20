from flask import redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from secure_it import login_required, make_layout
from database import get_user_by_email, update_user_by_email
from cloudinary_uploader import upload_profile_picture

YEAR_LEVELS = [
    "Grade 7",
    "Grade 8",
    "Grade 9",
    "Grade 10",
    "Grade 11",
    "Grade 12",
    "College First Year",
    "College Second Year",
    "College Third Year",
    "College Fourth Year",
]


def _render(message: str = "", error: str = ""):
    return make_layout(
        "profile",
        "Edit Profile",
        "Update your account details.",
        "profile.html",
        message=message,
        error=error,
        year_levels=YEAR_LEVELS,
    )


@login_required
def profile_page():
    if request.method != "POST":
        return _render()

    email = session.get("user_email", "")
    user = get_user_by_email(email)
    if not user:
        return _render(error="Could not load your account.")

    name = request.form.get("name", "").strip()
    year_level = request.form.get("year_level", "").strip()
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")
    profile_picture = request.files.get("profile_picture")

    if not name:
        return _render(error="Name cannot be empty.")

    updates = {"name": name, "year_level": year_level}

    if profile_picture and profile_picture.filename:
        if not getattr(profile_picture, "mimetype", "").startswith("image/"):
            return _render(error="Profile picture must be a JPG, PNG, or WEBP image.")

        uploaded_image = upload_profile_picture(profile_picture)
        if uploaded_image is None:
            return _render(error="Could not upload profile picture right now.")

        updates["profile_picture"] = uploaded_image

    if new_password or confirm_password or current_password:
        password_hash = user.get("password_hash")
        if not password_hash or not check_password_hash(password_hash, current_password):
            return _render(error="Current password is incorrect.")
        if new_password != confirm_password:
            return _render(error="New passwords do not match.")
        if len(new_password) < 6:
            return _render(error="New password must be at least 6 characters.")
        updates["password_hash"] = generate_password_hash(new_password)

    updated_user = update_user_by_email(email, updates)
    if not updated_user:
        return _render(error="Could not save your changes right now.")

    session["display_name"] = updated_user.get("name", name)
    session["year_level"] = updated_user.get("year_level", year_level)
    session["profile_picture"] = updated_user.get("profile_picture", session.get("profile_picture", ""))

    return redirect(url_for("profile_page", saved=1))
