from flask import redirect, request, session, url_for

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


def _current_profile() -> dict:
    email = session.get("user_email", "")
    user = get_user_by_email(email) if email else None
    if user:
        return {
            "name": user.get("name", ""),
            "email": user.get("email", email),
            "year_level": user.get("year_level", ""),
            "profile_picture": user.get("profile_picture", ""),
        }
    return {
        "name": session.get("display_name", ""),
        "email": email,
        "year_level": session.get("year_level", ""),
        "profile_picture": session.get("profile_picture", ""),
    }


@login_required
def profile_page():
    message = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        year_level = request.form.get("year_level", "").strip()
        profile_picture = request.files.get("profile_picture")

        if not name:
            error = "Name cannot be empty."
        elif year_level and year_level not in YEAR_LEVELS:
            error = "Please choose a valid year level."
        else:
            updates: dict[str, object] = {"name": name, "year_level": year_level}

            if profile_picture and profile_picture.filename:
                if not getattr(profile_picture, "mimetype", "").startswith("image/"):
                    error = "Profile picture must be a JPG, PNG, or WEBP image."
                else:
                    uploaded_image = upload_profile_picture(profile_picture)
                    if uploaded_image is None:
                        error = "Could not upload profile picture right now."
                    else:
                        updates["profile_picture"] = uploaded_image

            if error is None:
                update_user_by_email(session.get("user_email", ""), updates)
                session["display_name"] = name
                session["year_level"] = year_level
                if "profile_picture" in updates:
                    session["profile_picture"] = updates["profile_picture"]
                message = "Profile updated."

    profile = _current_profile()
    return make_layout(
        "profile",
        "Edit Profile",
        "Update your name, year level, and profile photo.",
        "profile.html",
        profile=profile,
        year_levels=YEAR_LEVELS,
        message=message,
        error=error,
    )
