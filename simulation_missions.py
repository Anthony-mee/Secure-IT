"""TryHackMe-style mission workspace definitions for Secure-IT simulations."""

from __future__ import annotations

from typing import Any

from simulation_data import ATTACKS, get_attack


def _base_mission(attack_id: str) -> dict[str, Any]:
    attack = get_attack(attack_id)
    if not attack:
        return {}

    overview = attack.get("overview", {})
    return {
        "attack_id": attack_id,
        "name": attack["name"],
        "icon": attack["icon"],
        "difficulty": attack["difficulty"],
        "mission_title": f"{attack['name']} Investigation",
        "story": overview.get("explanation", attack.get("short_description", "")),
        "objectives": [
            "Review intelligence briefing and available tools",
            "Investigate indicators in the simulated environment",
            "Identify malicious activity and document findings",
            "Submit the correct incident response action",
        ],
        "tools": ["inbox", "terminal", "url_analyzer", "logs", "scanner", "notes"],
        "estimated_minutes": 12 if attack["difficulty"] == "Beginner" else 18,
        "skills_learned": [
            "Threat identification",
            "Security analysis",
            "Incident response",
        ],
    }


WORKSPACE_MISSIONS: dict[str, dict[str, Any]] = {
    "phishing": {
        **_base_mission("phishing"),
        "mission_title": "Investigate a Suspicious Email Incident",
        "story": (
            "You are a junior cybersecurity analyst. An employee reported a suspicious email claiming their "
            "bank account will be locked. Investigate the message, analyze indicators, and determine the correct response."
        ),
        "objectives": [
            "Analyze email sender information",
            "Inspect message headers for spoofing",
            "Analyze suspicious URL indicators",
            "Review authentication logs for related activity",
            "Submit incident report with correct response",
        ],
        "skills_learned": [
            "Phishing identification",
            "Email header analysis",
            "URL threat assessment",
            "Incident reporting",
        ],
        "inbox": {
            "emails": [
                {
                    "id": "phish-1",
                    "from_display": "Secure Bank Support",
                    "from_address": "security@secure-bank-alert.com",
                    "subject": "URGENT: Verify your account now",
                    "body": "Dear customer,\n\nWe detected unusual activity. Your account will be locked in 60 minutes unless you verify your details.\n\nVerify here: http://secure-bank-verify.net/login\n\nSecure Banking Team",
                    "headers": {
                        "Return-Path": "security@secure-bank-alert.com",
                        "SPF": "FAIL — domain secure-bank-alert.com is not authorized",
                        "DKIM": "FAIL — signature invalid",
                        "Reply-To": "collections@unknown-mailer.io",
                    },
                    "suspicious_url": "http://secure-bank-verify.net/login",
                    "malicious": True,
                }
            ]
        },
        "logs": [
            {"time": "09:14:22", "level": "WARN", "message": "Outbound DNS lookup: secure-bank-verify.net"},
            {"time": "09:14:45", "level": "ALERT", "message": "User mailbox received external message with failed SPF"},
            {"time": "09:15:01", "level": "INFO", "message": "Proxy blocked category: newly-registered-domain"},
            {"time": "09:16:33", "level": "CRIT", "message": "Credential submission attempt to secure-bank-verify.net (simulated)"},
        ],
        "terminal_help": "Commands: help, whois <domain>, scan-url <url>, header-check, report-phishing",
        "terminal_responses": {
            "help": "Available: whois <domain>, scan-url <url>, header-check, report-phishing",
            "whois secure-bank-verify.net": "Domain created: 2 days ago\nRegistrar: ANONYMOUS REGISTRAR\nReputation: MALICIOUS",
            "scan-url http://secure-bank-verify.net/login": "Result: PHISHING\nCloned login page detected\nCredential harvesting form present",
            "header-check": "SPF: FAIL | DKIM: FAIL | Reply-To mismatch detected",
            "report-phishing": "Incident ticket SEC-2026-014 created. Email quarantined.",
        },
        "tasks": [
            {"id": "open_email", "objective_index": 0, "label": "Open the reported suspicious email", "tool": "inbox", "action": "open", "email_id": "phish-1"},
            {"id": "view_headers", "objective_index": 1, "label": "Inspect email headers", "tool": "inbox", "action": "headers", "email_id": "phish-1"},
            {"id": "scan_url", "objective_index": 2, "label": "Analyze the suspicious URL", "tool": "url_analyzer", "action": "analyze", "url": "http://secure-bank-verify.net/login"},
            {"id": "check_logs", "objective_index": 3, "label": "Review logs for related indicators", "tool": "logs", "action": "review"},
            {"id": "terminal_scan", "objective_index": 2, "label": "Run scan-url in terminal", "tool": "terminal", "action": "command", "command": "scan-url http://secure-bank-verify.net/login"},
            {"id": "submit_report", "objective_index": 4, "label": "Submit incident report: Report phishing", "tool": "notes", "action": "submit", "correct_response": "report_phishing"},
        ],
        "decisions": [
            {
                "id": "final_action",
                "prompt": "Based on your investigation, what is the correct response?",
                "options": [
                    {"id": "click", "label": "Click the link to verify the account", "score": 0, "mistake": "Clicked suspicious URL"},
                    {"id": "ignore", "label": "Ignore the email silently", "score": 50, "mistake": "Did not report phishing email"},
                    {"id": "report_phishing", "label": "Report phishing and quarantine the message", "score": 100, "good": "Reported malicious email and protected the organization"},
                ],
            }
        ],
    },
    "malware": {
        **_base_mission("malware"),
        "mission_title": "Malware Dropper Analysis Lab",
        "story": "A workstation flagged a suspicious download disguised as a media player update. Analyze the artifact and contain the threat.",
        "objectives": [
            "Scan suspicious executable in sandbox",
            "Review process and network indicators",
            "Identify malware behavior",
            "Recommend containment action",
        ],
        "inbox": {"files": [{"id": "mal-1", "name": "Update.exe", "hash": "a91f...c2", "size": "2.4 MB", "malicious": True}]},
        "logs": [
            {"time": "11:02:10", "level": "WARN", "message": "Unsigned binary executed from Downloads"},
            {"time": "11:02:44", "level": "ALERT", "message": "Suspicious outbound connection to 185.220.x.x"},
        ],
        "terminal_responses": {
            "help": "Commands: scan file.exe, netstat, quarantine Update.exe",
            "scan update.exe": "Result: MALWARE\nBehavior: keylogging, persistence registry key",
            "quarantine update.exe": "File isolated. Host contained.",
        },
        "tasks": [
            {"id": "scan_file", "objective_index": 0, "label": "Scan Update.exe in terminal", "tool": "terminal", "action": "command", "command": "scan update.exe"},
            {"id": "review_logs", "objective_index": 1, "label": "Review security logs", "tool": "logs", "action": "review"},
            {"id": "contain", "objective_index": 3, "label": "Quarantine malicious file", "tool": "terminal", "action": "command", "command": "quarantine update.exe"},
        ],
        "decisions": [
            {
                "id": "final_action",
                "prompt": "What is the best containment decision?",
                "options": [
                    {"id": "run", "label": "Run the update to test it", "score": 0, "mistake": "Executed unknown malware"},
                    {"id": "quarantine", "label": "Quarantine file and isolate host", "score": 100, "good": "Contained malware before spread"},
                    {"id": "ignore", "label": "Ignore antivirus warning", "score": 10, "mistake": "Ignored malware indicators"},
                ],
            }
        ],
    },
    "ransomware": {
        **_base_mission("ransomware"),
        "mission_title": "Ransomware Incident Response",
        "story": "Multiple file extensions changed across shared drives. Lead the initial response as the on-call analyst.",
        "objectives": ["Identify encryption indicators", "Isolate affected systems", "Preserve evidence", "Activate recovery plan"],
        "logs": [
            {"time": "03:18:01", "level": "CRIT", "message": "Mass file rename detected: *.locked"},
            {"time": "03:18:22", "level": "ALERT", "message": "Ransom note dropped on DESKTOP-FIN-04"},
        ],
        "terminal_responses": {
            "help": "Commands: isolate host, snapshot-logs, status",
            "isolate host": "Host removed from network. Lateral movement blocked.",
            "snapshot-logs": "Forensic snapshot saved to secure vault.",
        },
        "tasks": [
            {"id": "logs", "objective_index": 0, "label": "Review ransomware alerts", "tool": "logs", "action": "review"},
            {"id": "isolate", "objective_index": 1, "label": "Isolate affected host", "tool": "terminal", "action": "command", "command": "isolate host"},
            {"id": "snapshot", "objective_index": 2, "label": "Capture forensic snapshot", "tool": "terminal", "action": "command", "command": "snapshot-logs"},
        ],
        "decisions": [
            {
                "id": "final_action",
                "prompt": "What is the correct IR action?",
                "options": [
                    {"id": "pay", "label": "Pay ransom immediately", "score": 0, "mistake": "Paid ransom without IR process"},
                    {"id": "isolate_recover", "label": "Isolate systems and restore from backups", "score": 100, "good": "Followed proper ransomware response"},
                    {"id": "wait", "label": "Wait and monitor", "score": 15, "mistake": "Delayed containment during active encryption"},
                ],
            }
        ],
    },
}


def _generic_mission(attack_id: str) -> dict[str, Any]:
    attack = get_attack(attack_id)
    if not attack:
        return {}

    base = _base_mission(attack_id)
    steps = attack.get("steps", [])
    first = steps[0] if steps else {}
    iface = first.get("interface", {})

    base["story"] = attack.get("overview", {}).get("explanation", base["story"])
    base["mission_title"] = f"{attack['name']} Security Lab"
    base["logs"] = [
        {"time": "10:00:01", "level": "INFO", "message": f"Simulation environment ready: {attack_id}"},
        {"time": "10:00:15", "level": "WARN", "message": "Anomaly detected in training scenario"},
    ]
    base["terminal_responses"] = {
        "help": "Commands: analyze, scan, report",
        "analyze": "Analysis complete. Review indicators in logs panel.",
        "scan": "Scan complete. Suspicious activity confirmed in scenario.",
        "report": "Incident report submitted to SOC queue.",
    }
    base["inbox"] = {
        "emails": [
            {
                "id": f"{attack_id}-1",
                "from_display": "Training Scenario",
                "from_address": f"lab@{attack_id}.secure-it.local",
                "subject": first.get("title", attack["name"]),
                "body": first.get("narrative", attack["short_description"]),
                "headers": {"SPF": "PASS", "Scenario": attack["name"]},
                "suspicious_url": iface.get("highlight") or iface.get("url", ""),
                "malicious": True,
            }
        ]
    }
    base["tasks"] = [
        {"id": "investigate", "objective_index": 1, "label": "Investigate scenario indicators", "tool": "logs", "action": "review"},
        {"id": "analyze", "objective_index": 2, "label": "Run analyze in terminal", "tool": "terminal", "action": "command", "command": "analyze"},
        {"id": "report", "objective_index": 3, "label": "Submit incident report", "tool": "terminal", "action": "command", "command": "report"},
    ]
    best_choice = next((c for step in steps for c in step.get("choices", []) if c.get("is_best")), None)
    base["decisions"] = [
        {
            "id": "final_action",
            "prompt": first.get("narrative", "Choose the best security response."),
            "options": [
                {
                    "id": c["id"],
                    "label": c["label"],
                    "score": c.get("score", 0),
                    "good": c["label"] if c.get("is_best") or c.get("score", 0) >= 100 else None,
                    "mistake": c["label"] if c.get("score", 0) < 70 else None,
                }
                for step in steps[:1]
                for c in step.get("choices", [])
            ]
            or [
                {"id": "secure", "label": "Apply secure response", "score": 100, "good": "Selected secure response"},
                {"id": "risky", "label": "Take risky shortcut", "score": 0, "mistake": "Unsafe decision"},
            ],
        }
    ]
    if best_choice:
        base["decisions"][0]["options"] = sorted(
            base["decisions"][0]["options"],
            key=lambda o: o.get("score", 0),
            reverse=True,
        )
    return base


def get_workspace_mission(attack_id: str) -> dict[str, Any] | None:
    if attack_id in WORKSPACE_MISSIONS:
        mission = dict(WORKSPACE_MISSIONS[attack_id])
    else:
        mission = _generic_mission(attack_id)

    if not mission:
        return None

    attack = get_attack(attack_id)
    if attack:
        mission["quiz"] = attack.get("quiz", [])
        mission["short_description"] = attack.get("short_description", "")
    return mission


def list_mission_summaries() -> list[dict[str, Any]]:
    summaries = []
    for attack_id in ATTACKS:
        mission = get_workspace_mission(attack_id)
        if not mission:
            continue
        summaries.append(
            {
                "id": attack_id,
                "name": mission["name"],
                "icon": mission["icon"],
                "difficulty": mission["difficulty"],
                "short_description": mission.get("short_description", ""),
                "mission_title": mission["mission_title"],
                "estimated_minutes": mission["estimated_minutes"],
                "objectives_count": len(mission.get("objectives", [])),
                "skills_learned": mission.get("skills_learned", []),
                "tools": mission.get("tools", []),
            }
        )
    return summaries
