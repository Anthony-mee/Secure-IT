import json
import time

from flask import abort, jsonify, redirect, request, session, url_for

from database import get_user_progress, record_simulation_completion
from secure_it import login_required, make_layout
from simulation_missions import get_workspace_mission, list_mission_summaries


def _require_mission(attack_id: str):
    mission = get_workspace_mission(attack_id)
    if not mission:
        abort(404)
    return mission


@login_required
def simulations_page():
    progress = get_user_progress(session.get("user_email", ""))
    return make_layout(
        "simulations",
        "Cyber Range",
        "Select a mission room, review the briefing, then enter the interactive workspace.",
        "simulations.html",
        attacks=list_mission_summaries(),
        progress=progress,
    )


@login_required
def simulation_overview_page(attack_id: str):
    mission = _require_mission(attack_id)
    progress = get_user_progress(session.get("user_email", ""))
    completed = attack_id in progress.get("simulations_completed", [])
    return make_layout(
        "simulations",
        mission["mission_title"],
        "Mission briefing — review objectives before entering the lab.",
        "simulation_mission.html",
        mission=mission,
        completed=completed,
    )


@login_required
def simulation_start_page(attack_id: str):
    _require_mission(attack_id)
    session[f"sim_started_{attack_id}"] = True
    session[f"sim_started_at_{attack_id}"] = int(time.time())
    session.pop(f"sim_result_{attack_id}", None)
    session.pop(f"quiz_result_{attack_id}", None)
    return redirect(url_for("simulation_play_page", attack_id=attack_id))


@login_required
def simulation_play_page(attack_id: str):
    mission = _require_mission(attack_id)
    if not session.get(f"sim_started_{attack_id}"):
        return redirect(url_for("simulation_overview_page", attack_id=attack_id))

    workspace_payload = {
        "attack_id": mission["attack_id"],
        "name": mission["name"],
        "mission_title": mission["mission_title"],
        "objectives": mission.get("objectives", []),
        "tools": mission.get("tools", []),
        "skills_learned": mission.get("skills_learned", []),
        "inbox": mission.get("inbox", {}),
        "logs": mission.get("logs", []),
        "terminal_responses": mission.get("terminal_responses", {}),
        "terminal_help": mission.get("terminal_help", "Type help"),
        "tasks": mission.get("tasks", []),
        "decisions": mission.get("decisions", []),
        "complete_url": url_for("simulation_complete_page", attack_id=attack_id),
        "briefing_url": url_for("simulation_overview_page", attack_id=attack_id),
    }

    return make_layout(
        "simulations",
        mission["mission_title"],
        "Interactive investigation workspace",
        "simulation_workspace.html",
        mission=mission,
        workspace_json=json.dumps(workspace_payload),
    )


@login_required
def simulation_complete_page(attack_id: str):
    mission = _require_mission(attack_id)
    if request.method != "POST":
        return redirect(url_for("simulation_play_page", attack_id=attack_id))

    payload = request.get_json(silent=True) or {}
    score = max(0, min(100, int(payload.get("score", 0))))
    good_decisions = list(payload.get("good_decisions", []))
    mistakes = list(payload.get("mistakes", []))
    recommendations = list(payload.get("recommendations", []))
    actions_log = list(payload.get("actions_log", []))
    time_spent_seconds = int(payload.get("time_spent_seconds", 0))
    skills_developed = list(payload.get("skills_developed", mission.get("skills_learned", [])))

    started_at = session.get(f"sim_started_at_{attack_id}")
    if started_at and not time_spent_seconds:
        time_spent_seconds = max(0, int(time.time()) - int(started_at))

    points_earned = max(10, score // 2)
    result = {
        "score": score,
        "good_decisions": good_decisions,
        "mistakes": mistakes,
        "recommendations": recommendations,
        "points_earned": points_earned,
        "time_spent_seconds": time_spent_seconds,
        "skills_developed": skills_developed,
        "actions_log": actions_log,
    }
    session[f"sim_result_{attack_id}"] = result

    email = session.get("user_email")
    if email:
        user = record_simulation_completion(
            email,
            attack_id,
            simulation_score=score,
            points_earned=points_earned,
            mistakes=mistakes,
            good_actions=good_decisions,
            time_spent_seconds=time_spent_seconds,
            actions_log=actions_log,
            skills_developed=skills_developed,
        )
        if user:
            session["display_name"] = user.get("name", session.get("display_name"))

    return jsonify({"success": True, "redirect": url_for("simulation_results_page", attack_id=attack_id)})


@login_required
def simulation_results_page(attack_id: str):
    mission = _require_mission(attack_id)
    result = session.get(f"sim_result_{attack_id}")
    if not result:
        return redirect(url_for("simulation_overview_page", attack_id=attack_id))

    minutes = result.get("time_spent_seconds", 0) // 60
    seconds = result.get("time_spent_seconds", 0) % 60

    return make_layout(
        "simulations",
        "Mission Debrief",
        f"Performance report for {mission['name']}.",
        "simulation_results.html",
        mission=mission,
        result=result,
        time_display=f"{minutes}m {seconds}s",
    )


@login_required
def simulation_quiz_page(attack_id: str):
    mission = _require_mission(attack_id)
    if not session.get(f"sim_result_{attack_id}"):
        return redirect(url_for("simulation_overview_page", attack_id=attack_id))

    quiz_data = {
        "attack_id": mission["attack_id"],
        "name": mission["name"],
        "questions": mission.get("quiz", []),
        "submit_url": url_for("simulation_quiz_submit_page", attack_id=attack_id),
        "simulations_url": url_for("simulations_page"),
    }
    return make_layout(
        "simulations",
        f"{mission['name']} Quiz",
        "Scenario-based knowledge check",
        "simulation_quiz.html",
        mission=mission,
        quiz_data_json=json.dumps(quiz_data),
    )


@login_required
def simulation_quiz_submit_page(attack_id: str):
    mission = _require_mission(attack_id)
    if request.method != "POST":
        return redirect(url_for("simulation_quiz_page", attack_id=attack_id))

    payload = request.get_json(silent=True) or {}
    answers = payload.get("answers", [])
    questions = mission.get("quiz", [])
    correct_count = 0
    feedback = []

    for index, question in enumerate(questions):
        try:
            selected = int(answers[index]) if index < len(answers) else -1
        except (TypeError, ValueError):
            selected = -1
        is_correct = selected == question["correct"]
        if is_correct:
            correct_count += 1
        feedback.append(
            {
                "question": question["question"],
                "correct": is_correct,
                "explanation": question["explanation"],
                "selected": selected,
                "correct_index": question["correct"],
                "options": question["options"],
            }
        )

    total = len(questions) or 1
    quiz_score = round((correct_count / total) * 100)
    quiz_points = max(5, quiz_score // 3)

    sim_result = session.get(f"sim_result_{attack_id}", {})
    session[f"quiz_result_{attack_id}"] = {
        "score": quiz_score,
        "correct_count": correct_count,
        "total": total,
        "feedback": feedback,
        "points_earned": quiz_points,
    }

    email = session.get("user_email")
    if email:
        record_simulation_completion(
            email,
            attack_id,
            simulation_score=int(sim_result.get("score", 0)),
            quiz_score=quiz_score,
            points_earned=quiz_points,
            mistakes=sim_result.get("mistakes", []),
            good_actions=sim_result.get("good_decisions", []),
            time_spent_seconds=int(sim_result.get("time_spent_seconds", 0)),
            skills_developed=sim_result.get("skills_developed", []),
        )

    return jsonify(
        {
            "success": True,
            "score": quiz_score,
            "correct_count": correct_count,
            "total": total,
            "points_earned": quiz_points,
            "feedback": feedback,
            "redirect": url_for("simulations_page"),
        }
    )
