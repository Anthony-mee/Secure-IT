from flask import session

from database import get_user_dashboard_data
from secure_it import login_required, make_layout
from simulation_missions import list_mission_summaries


DEFAULT_MODULES = [
    {"title": "Phishing Awareness", "description": "Identify deceptive messages and protect credentials.", "status": "In Progress", "points": 120},
    {"title": "Password Security", "description": "Build strong authentication habits and MFA awareness.", "status": "Not Started", "points": 100},
    {"title": "Malware Defense", "description": "Recognize malicious downloads and infection paths.", "status": "Not Started", "points": 140},
    {"title": "Social Engineering", "description": "Resist manipulation and verify identities.", "status": "Not Started", "points": 130},
]


@login_required
def dashboard_page():
    email = session.get("user_email", "")
    data = get_user_dashboard_data(email)
    missions = list_mission_summaries()
    completed = set(data["simulations_completed"])

    recommended = [m for m in missions if m["id"] not in completed][:3]
    if not recommended:
        recommended = missions[:3]

    modules = []
    for index, module in enumerate(DEFAULT_MODULES):
        status = "Completed" if index < len(completed) else module["status"]
        if index == len(completed) and completed:
            status = "In Progress"
        modules.append({**module, "status": status})

    profile = {
        "name": data["name"],
        "level": data["level"],
        "points": data["points"],
        "badges": data["badges"],
        "completion": data["completion"],
    }

    return make_layout(
        "dashboard",
        "Learning Dashboard",
        "Your personal cybersecurity training hub.",
        "dashboard.html",
        profile=profile,
        metrics=data["metrics"],
        modules=modules,
        history=data["history"],
        recommended=recommended,
        average_score=data["average_score"],
    )
