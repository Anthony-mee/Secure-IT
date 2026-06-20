"""Cybersecurity attack simulation content for Secure-IT."""

from __future__ import annotations

from typing import Any


def _choice(
    choice_id: str,
    label: str,
    outcome: str,
    explanation: str,
    score: int,
    is_best: bool = False,
) -> dict[str, Any]:
    return {
        "id": choice_id,
        "label": label,
        "outcome": outcome,
        "explanation": explanation,
        "score": score,
        "is_best": is_best,
    }


ATTACKS: dict[str, dict[str, Any]] = {
    "phishing": {
        "id": "phishing",
        "name": "Phishing Attack",
        "icon": "🎣",
        "difficulty": "Beginner",
        "short_description": "Learn to spot fake emails and messages designed to steal your credentials.",
        "overview": {
            "explanation": (
                "Phishing is a cyber attack where attackers impersonate trusted organizations or individuals "
                "to trick users into revealing sensitive information such as passwords, financial details, or personal data."
            ),
            "why_used": "Attackers use phishing because it is cheap, scalable, and exploits human trust rather than technical flaws.",
            "how_encountered": "You may encounter phishing through email, SMS, social media messages, or fake login pages.",
            "how_it_happens": [
                "Attacker creates a fake message or email that looks legitimate.",
                "Victim receives the suspicious communication.",
                "Victim clicks a malicious link or provides sensitive information.",
                "Attacker gains access to accounts, money, or personal data.",
            ],
            "warning_signs": [
                "Suspicious or shortened links",
                "Urgent language demanding immediate action",
                "Unknown or spoofed senders",
                "Requests for passwords or personal information",
                "Fake websites with slightly wrong URLs",
            ],
            "prevention_tips": [
                "Verify links before clicking by hovering or checking the domain",
                "Enable multi-factor authentication on important accounts",
                "Never share passwords through email or chat",
                "Check sender identity through official channels",
            ],
        },
        "steps": [
            {
                "title": "Suspicious Bank Email",
                "narrative": "You receive an email claiming to be from your bank saying your account will be locked unless you verify your information within one hour.",
                "interface_type": "email",
                "interface": {
                    "from": "security@secure-bank-alert.com",
                    "subject": "URGENT: Verify your account now",
                    "body": "Dear customer,\n\nWe detected unusual activity. Your account will be locked in 60 minutes unless you verify your details.\n\nClick here: http://secure-bank-verify.net/login\n\nSecure Banking Team",
                    "highlight": "http://secure-bank-verify.net/login",
                },
                "choices": [
                    _choice(
                        "click",
                        "Click the verification link",
                        "You entered credentials on a fake site. The attacker captured your username and password.",
                        "The link domain does not match your real bank. Phishing sites mimic legitimate login pages to steal credentials.",
                        0,
                    ),
                    _choice(
                        "report",
                        "Report the email to IT or your bank",
                        "You flagged a phishing attempt. Security teams can warn others and block the malicious domain.",
                        "Reporting suspicious messages is the best response. It protects you and helps your organization respond quickly.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "ignore",
                        "Ignore the message",
                        "You avoided the trap, but the phishing email remains unreported and may target others.",
                        "Ignoring is safer than clicking, but reporting helps stop the attack from spreading.",
                        60,
                    ),
                ],
            },
            {
                "title": "Follow-up Login Page",
                "narrative": "You opened the link in a sandbox browser. A login page appears asking for your banking username, password, and OTP code.",
                "interface_type": "website",
                "interface": {
                    "url": "http://secure-bank-verify.net/login",
                    "title": "Secure Bank — Account Verification",
                    "fields": ["Username", "Password", "One-time code"],
                },
                "choices": [
                    _choice(
                        "enter",
                        "Enter your credentials to verify",
                        "Credentials were sent to the attacker. Your account is now compromised.",
                        "Legitimate banks do not ask for full credentials on pages reached through urgent email links.",
                        0,
                    ),
                    _choice(
                        "close",
                        "Close the page and report the URL",
                        "You stopped the attack and provided valuable intelligence to your security team.",
                        "Closing suspicious pages and reporting URLs prevents credential theft.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "bookmark",
                        "Bookmark the page to check later",
                        "You preserved a dangerous link that could be clicked accidentally later.",
                        "Never bookmark unverified login pages. Delete the email and report it instead.",
                        20,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "You receive an email asking you to verify your account through a link. What should you do?",
                "options": [
                    "Click immediately before the account is locked",
                    "Reply with your password to prove ownership",
                    "Verify the sender through official channels and avoid suspicious links",
                    "Forward the email to classmates for advice",
                ],
                "correct": 2,
                "explanation": "Legitimate organizations will not usually request passwords through email links. Verify through official apps or phone numbers.",
            },
            {
                "question": "Which sign most strongly suggests a phishing email?",
                "options": [
                    "Professional company logo",
                    "Generic greeting like 'Dear customer'",
                    "Email sent during business hours",
                    "Plain text formatting",
                ],
                "correct": 1,
                "explanation": "Generic greetings and urgent threats are common phishing indicators, especially combined with suspicious links.",
            },
            {
                "question": "What is the safest first action after spotting phishing?",
                "options": ["Click to see if the page loads", "Report it and delete the message", "Reply asking if it is real", "Ignore forever without telling anyone"],
                "correct": 1,
                "explanation": "Reporting helps security teams protect others. Deleting after reporting reduces accidental clicks.",
            },
        ],
    },
    "malware": {
        "id": "malware",
        "name": "Malware",
        "icon": "🦠",
        "difficulty": "Beginner",
        "short_description": "Understand malicious software that infects devices and steals or destroys data.",
        "overview": {
            "explanation": "Malware is malicious software designed to damage systems, steal data, spy on users, or give attackers remote control.",
            "why_used": "Attackers deploy malware to steal credentials, encrypt files for ransom, or build botnets.",
            "how_encountered": "Malware often arrives through downloads, email attachments, pirated software, or infected USB drives.",
            "how_it_happens": [
                "Victim downloads or opens an infected file.",
                "Malware installs silently in the background.",
                "It spreads, steals data, or disrupts the system.",
                "Victim discovers damage or performance issues later.",
            ],
            "warning_signs": [
                "Unexpected pop-ups or browser changes",
                "Slow device performance",
                "Unknown programs running at startup",
                "Antivirus disabled without your action",
                "Files appearing encrypted or missing",
            ],
            "prevention_tips": [
                "Download software only from official sources",
                "Keep operating systems and antivirus updated",
                "Scan attachments before opening",
                "Avoid pirated or cracked software",
            ],
        },
        "steps": [
            {
                "title": "Suspicious Download Prompt",
                "narrative": "A pop-up says your media player is outdated and offers a 'free update' from an unofficial website.",
                "interface_type": "popup",
                "interface": {
                    "title": "Flash Player Update Required",
                    "message": "Install the update now to continue watching videos.",
                    "button": "Download Update.exe",
                },
                "choices": [
                    _choice(
                        "download",
                        "Download and run the update",
                        "Malware installed itself and began logging keystrokes on your device.",
                        "Unofficial update prompts are a classic malware delivery method.",
                        0,
                    ),
                    _choice(
                        "close",
                        "Close the pop-up and run an antivirus scan",
                        "You avoided infection and checked your system for threats.",
                        "Closing suspicious pop-ups and scanning protects against drive-by downloads.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "ignore_once",
                        "Ignore it this time but keep browsing",
                        "You avoided this prompt, but similar traps may appear on unsafe sites.",
                        "Unsafe browsing habits increase the chance of future malware infection.",
                        50,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "What is malware?",
                "options": ["Helpful system optimization software", "Malicious software designed to harm or exploit", "A type of secure cloud backup", "Hardware that speeds up your PC"],
                "correct": 1,
                "explanation": "Malware is intentionally harmful software such as viruses, trojans, ransomware, and spyware.",
            },
            {
                "question": "Which action best reduces malware risk?",
                "options": ["Disable antivirus for speed", "Download from official trusted sources", "Open all email attachments", "Use unknown USB drives found in public"],
                "correct": 1,
                "explanation": "Trusted sources and updated security software are core defenses against malware.",
            },
        ],
    },
    "ransomware": {
        "id": "ransomware",
        "name": "Ransomware",
        "icon": "🔒",
        "difficulty": "Intermediate",
        "short_description": "Experience how attackers encrypt files and demand payment to restore access.",
        "overview": {
            "explanation": "Ransomware encrypts your files or locks your system, then demands payment—often in cryptocurrency—to restore access.",
            "why_used": "Attackers profit directly by extorting victims who need their files back urgently.",
            "how_encountered": "Ransomware spreads through phishing emails, exposed remote access, or unpatched software.",
            "how_it_happens": [
                "Malware gains access to the system.",
                "It encrypts files across drives and network shares.",
                "A ransom note appears with payment instructions.",
                "Victims face data loss if backups are unavailable.",
            ],
            "warning_signs": [
                "Unexpected file extension changes",
                "Ransom notes on desktop or in folders",
                "Inability to open documents",
                "Mass antivirus alerts",
                "Demands for cryptocurrency payment",
            ],
            "prevention_tips": [
                "Maintain regular offline backups",
                "Patch systems promptly",
                "Limit user permissions",
                "Never pay ransoms without consulting IT—payment does not guarantee recovery",
            ],
        },
        "steps": [
            {
                "title": "Encrypted Files Alert",
                "narrative": "Your project folder files now have a strange extension. A note demands payment in Bitcoin within 48 hours.",
                "interface_type": "ransom",
                "interface": {
                    "headline": "YOUR FILES HAVE BEEN ENCRYPTED",
                    "message": "Pay 0.5 BTC to recover your documents. Timer: 47:59:12 remaining.",
                    "files": ["report.docx.locked", "presentation.pptx.locked", "notes.pdf.locked"],
                },
                "choices": [
                    _choice(
                        "pay",
                        "Pay the ransom immediately",
                        "Payment was sent but files were not restored. Attackers often re-target paying victims.",
                        "Paying encourages criminals and rarely guarantees full recovery.",
                        0,
                    ),
                    _choice(
                        "isolate",
                        "Disconnect from the network and contact IT",
                        "IT isolated the device, restored from backups, and blocked further spread.",
                        "Isolation and professional response limit damage and preserve recoverable backups.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "wait",
                        "Wait to see if files fix themselves",
                        "Ransomware spread to shared drives while you waited.",
                        "Delay allows ransomware to encrypt more systems. Act immediately.",
                        10,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "What does ransomware primarily do?",
                "options": ["Speeds up your computer", "Encrypts files and demands payment", "Improves file compression", "Updates your antivirus"],
                "correct": 1,
                "explanation": "Ransomware holds data hostage by encryption until a ransom is paid.",
            },
            {
                "question": "Best defense against ransomware data loss?",
                "options": ["Regular tested backups", "Stronger passwords only", "Disabling firewalls", "Paying quickly every time"],
                "correct": 0,
                "explanation": "Reliable backups let organizations recover without paying criminals.",
            },
        ],
    },
    "trojan": {
        "id": "trojan",
        "name": "Trojan Horse",
        "icon": "🐴",
        "difficulty": "Intermediate",
        "short_description": "Discover how harmful programs hide inside seemingly useful software.",
        "overview": {
            "explanation": "A trojan disguises itself as legitimate software while performing hidden malicious actions in the background.",
            "why_used": "Trojans trick users into installing them willingly, bypassing some technical defenses.",
            "how_encountered": "They appear as game mods, cracked tools, fake utilities, or malicious email attachments.",
            "how_it_happens": [
                "User installs what appears to be helpful software.",
                "The trojan runs hidden tasks such as spying or backdoor access.",
                "Attackers use the backdoor to steal data or install more malware.",
                "The victim may not notice until damage occurs.",
            ],
            "warning_signs": [
                "Software from unofficial websites",
                "Requests for excessive permissions",
                "Unexpected network activity",
                "Unknown processes after installing 'free tools'",
            ],
            "prevention_tips": [
                "Verify software publishers and digital signatures",
                "Use official app stores when possible",
                "Review permissions before installing",
                "Scan downloads before execution",
            ],
        },
        "steps": [
            {
                "title": "Free Game Cheat Tool",
                "narrative": "A forum user shares a 'free premium unlock tool' for a popular game. It requires administrator access to install.",
                "interface_type": "installer",
                "interface": {
                    "name": "GameBoost_Pro_Setup.exe",
                    "publisher": "Unknown Publisher",
                    "warning": "Windows protected your PC — unverified publisher",
                },
                "choices": [
                    _choice(
                        "install",
                        "Run as administrator anyway",
                        "A backdoor was installed. Attackers now have remote access to your system.",
                        "Trojans often request admin rights to embed deeply in the system.",
                        0,
                    ),
                    _choice(
                        "reject",
                        "Cancel installation and delete the file",
                        "You removed the trojan before it could execute.",
                        "Rejecting unverified software is the correct response.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "scan",
                        "Install but run antivirus afterward",
                        "The trojan may have already disabled security tools during install.",
                        "Prevention beats cleanup—do not install suspicious executables.",
                        30,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "Why is it called a Trojan horse?",
                "options": ["It spreads through horses", "It hides harm inside something that looks useful", "It only affects ancient systems", "It encrypts all files instantly"],
                "correct": 1,
                "explanation": "Like the myth, trojans conceal malicious intent inside appealing packages.",
            },
        ],
    },
    "virus": {
        "id": "virus",
        "name": "Computer Virus",
        "icon": "🧬",
        "difficulty": "Beginner",
        "short_description": "Learn how self-replicating code spreads between files and devices.",
        "overview": {
            "explanation": "A computer virus attaches to legitimate programs or files and spreads when those files are shared or executed.",
            "why_used": "Viruses propagate through user activity, infecting networks and removable media.",
            "how_encountered": "Shared documents, infected USB drives, and legacy email attachments are common vectors.",
            "how_it_happens": [
                "User opens an infected file or program.",
                "The virus copies itself to other files or systems.",
                "Infected files spread through shares, email, or drives.",
                "Systems show corruption, crashes, or data loss.",
            ],
            "warning_signs": [
                "Files behaving strangely or corrupting",
                "Antivirus alerts on shared documents",
                "Programs launching without input",
                "Friends reporting infections from your shared files",
            ],
            "prevention_tips": [
                "Scan removable media before use",
                "Avoid sharing unverified files",
                "Keep antivirus definitions updated",
                "Disable auto-run on external drives",
            ],
        },
        "steps": [
            {
                "title": "USB Drive Found",
                "narrative": "You find a USB drive labeled 'Project Files' in the school lab. Your classmate asks you to plug it in to see what's inside.",
                "interface_type": "device",
                "interface": {
                    "label": "USB Drive (E:)",
                    "files": ["Project_Final.exe", "readme.txt"],
                    "autorun": "Auto-play prompt enabled",
                },
                "choices": [
                    _choice(
                        "open",
                        "Open Project_Final.exe immediately",
                        "The executable contained a virus that began infecting files on your laptop.",
                        "Unknown executables on found drives are high-risk infection sources.",
                        0,
                    ),
                    _choice(
                        "scan",
                        "Hand to IT for scanning in an isolated environment",
                        "IT found a virus and safely removed it without infecting the network.",
                        "Professional scanning prevents outbreaks from unknown media.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "view",
                        "Open only the text file",
                        "The text file referenced the executable, which you opened next and got infected.",
                        "Even companion files can social-engineer users into running malware.",
                        25,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "How do computer viruses typically spread?",
                "options": ["Through infected files and shared media", "Only through power outages", "By improving CPU speed", "Through legitimate OS updates only"],
                "correct": 0,
                "explanation": "Viruses replicate by attaching to files and spreading when those files move between systems.",
            },
        ],
    },
    "spyware": {
        "id": "spyware",
        "name": "Spyware",
        "icon": "👁️",
        "difficulty": "Intermediate",
        "short_description": "See how hidden software monitors activity and steals private information.",
        "overview": {
            "explanation": "Spyware secretly monitors user activity, capturing keystrokes, screenshots, browsing history, and credentials.",
            "why_used": "Attackers harvest personal and financial data for fraud or resale.",
            "how_encountered": "Bundled with free software, malicious browser extensions, or compromised downloads.",
            "how_it_happens": [
                "Spyware installs alongside another program.",
                "It runs silently in the background.",
                "It logs sensitive input and sends data to attackers.",
                "Victims discover fraud or privacy breaches later.",
            ],
            "warning_signs": [
                "Battery drain or sluggish performance",
                "Unknown browser extensions",
                "Unexpected webcam or microphone activity",
                "Unexplained account logins from new locations",
            ],
            "prevention_tips": [
                "Review installed browser extensions regularly",
                "Use reputable security software",
                "Cover cameras when not in use and audit app permissions",
                "Avoid suspicious free toolbars and utilities",
            ],
        },
        "steps": [
            {
                "title": "Free Screen Recorder Extension",
                "narrative": "A browser extension promises free HD screen recording but asks for access to all website data and clipboard content.",
                "interface_type": "extension",
                "interface": {
                    "name": "UltraCapture Free",
                    "permissions": ["Read all data on all websites", "Access clipboard", "Manage downloads"],
                    "reviews": "Mixed — some users report account theft",
                },
                "choices": [
                    _choice(
                        "add",
                        "Add extension with full permissions",
                        "Spyware began logging passwords and session tokens from banking sites.",
                        "Excessive permissions are a major spyware red flag.",
                        0,
                    ),
                    _choice(
                        "decline",
                        "Decline and use a trusted official tool instead",
                        "You avoided spyware and used a verified screen recorder from the official store.",
                        "Minimal permissions and trusted publishers reduce spyware risk.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "limited",
                        "Add it but never visit banking sites",
                        "Spyware still captured credentials from email and school accounts.",
                        "Spyware monitors broadly—not just banking sessions.",
                        35,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "What is spyware designed to do?",
                "options": ["Improve graphics performance", "Secretly monitor and collect user data", "Encrypt files for backup", "Block all internet ads"],
                "correct": 1,
                "explanation": "Spyware operates covertly to capture sensitive information.",
            },
        ],
    },
    "dos": {
        "id": "dos",
        "name": "Denial of Service (DoS)",
        "icon": "⚡",
        "difficulty": "Advanced",
        "short_description": "Understand attacks that overwhelm systems and make services unavailable.",
        "overview": {
            "explanation": "Denial of Service attacks flood servers or networks with traffic so legitimate users cannot access services.",
            "why_used": "Attackers disrupt operations, extort organizations, or distract from other intrusions.",
            "how_encountered": "Users experience outages; defenders see traffic spikes and failed logins at scale.",
            "how_it_happens": [
                "Attackers coordinate massive traffic or requests.",
                "Servers exhaust CPU, memory, or bandwidth.",
                "Services slow down or become unreachable.",
                "Business and learning activities are disrupted.",
            ],
            "warning_signs": [
                "Sudden site slowness or timeouts",
                "Spike in failed login attempts",
                "Unusual traffic from many IP addresses",
                "Monitoring alerts for resource exhaustion",
            ],
            "prevention_tips": [
                "Use DDoS mitigation services",
                "Rate-limit authentication endpoints",
                "Monitor network traffic patterns",
                "Report outages to IT immediately",
            ],
        },
        "steps": [
            {
                "title": "School Portal Outage",
                "narrative": "The learning portal is extremely slow. IT suspects a DoS attack is targeting the login page during exam week.",
                "interface_type": "status",
                "interface": {
                    "service": "Secure-IT Learning Portal",
                    "status": "Degraded — 98% request failure",
                    "chart": "Traffic spike from botnet sources",
                },
                "choices": [
                    _choice(
                        "retry",
                        "Refresh the login page hundreds of times",
                        "Your retries added to the traffic flood and made recovery harder.",
                        "Repeated requests during an outage can unintentionally worsen DoS conditions.",
                        0,
                    ),
                    _choice(
                        "notify",
                        "Notify IT and use official status updates",
                        "IT activated mitigation and communicated alternate access paths.",
                        "Coordinated response and patience help organizations recover from DoS attacks.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "share",
                        "Share the login link in group chats repeatedly",
                        "More users hammered the failing service, increasing load.",
                        "During outages, avoid amplifying traffic to struggling systems.",
                        20,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "What is the main goal of a DoS attack?",
                "options": ["Steal passwords silently", "Make services unavailable to users", "Improve server performance", "Install antivirus software"],
                "correct": 1,
                "explanation": "DoS attacks target availability by overwhelming systems with traffic.",
            },
        ],
    },
    "social_engineering": {
        "id": "social_engineering",
        "name": "Social Engineering",
        "icon": "🎭",
        "difficulty": "Intermediate",
        "short_description": "Practice responding to manipulative tactics that exploit trust and urgency.",
        "overview": {
            "explanation": "Social engineering manipulates people into revealing information or taking unsafe actions through psychology rather than hacking alone.",
            "why_used": "Humans are often the weakest link—urgency, authority, and fear bypass technical controls.",
            "how_encountered": "Phone calls, impersonation, tailgating, fake IT support, and urgent messages.",
            "how_it_happens": [
                "Attacker researches the target or organization.",
                "They impersonate someone trusted.",
                "They create urgency or fear to rush decisions.",
                "Victim shares credentials or access.",
            ],
            "warning_signs": [
                "Unusual urgency or secrecy requests",
                "Callers refusing to verify identity",
                "Requests to bypass normal procedures",
                "Pressure to share OTP codes",
            ],
            "prevention_tips": [
                "Verify identity through official channels",
                "Follow established security procedures",
                "Never share MFA codes with anyone",
                "Report suspicious contact attempts",
            ],
        },
        "steps": [
            {
                "title": "Urgent IT Support Call",
                "narrative": "Someone calling from an unknown number claims to be IT support. They say your account will be deleted in 10 minutes unless you read them your verification code.",
                "interface_type": "phone",
                "interface": {
                    "caller": "Unknown Number",
                    "script": "Hi, this is IT. We detected a breach on your account. Read me the 6-digit code we just sent you so we can secure it.",
                },
                "choices": [
                    _choice(
                        "code",
                        "Read the verification code aloud",
                        "The attacker used your code to reset your password and access your account.",
                        "MFA codes should never be shared—legitimate IT will never ask for them.",
                        0,
                    ),
                    _choice(
                        "verify",
                        "Hang up and call IT through the official helpdesk number",
                        "Real IT confirmed there was no breach. The social engineering attempt was logged.",
                        "Independent verification defeats impersonation attacks.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "partial",
                        "Give them your username but not the code",
                        "They used your username to trigger more targeted phishing against you.",
                        "Even partial information helps attackers refine their approach.",
                        40,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "Social engineering primarily targets:",
                "options": ["Hardware cooling systems", "Human psychology and trust", "Fiber optic cables", "Power supply units"],
                "correct": 1,
                "explanation": "Social engineering exploits human behavior rather than software bugs alone.",
            },
        ],
    },
    "password_attack": {
        "id": "password_attack",
        "name": "Password Attack",
        "icon": "🔑",
        "difficulty": "Beginner",
        "short_description": "Test weak passwords and learn how attackers crack or guess credentials.",
        "overview": {
            "explanation": "Password attacks use guessing, stolen lists, or brute force to break into accounts protected by weak or reused passwords.",
            "why_used": "Weak passwords are easy to crack and often reused across multiple sites.",
            "how_encountered": "Failed login alerts, account lockouts, or notifications of logins from unknown devices.",
            "how_it_happens": [
                "Attacker obtains leaked password lists or guesses common passwords.",
                "Automated tools try thousands of combinations.",
                "Successful guesses grant account access.",
                "Reused passwords compromise multiple services.",
            ],
            "warning_signs": [
                "Passwords based on names or dates",
                "Same password on many accounts",
                "Short passwords under 12 characters",
                "Passwords never changed after a breach alert",
            ],
            "prevention_tips": [
                "Use long unique passwords or passphrases",
                "Enable multi-factor authentication",
                "Use a reputable password manager",
                "Change passwords after known breaches",
            ],
        },
        "steps": [
            {
                "title": "Weak Password Challenge",
                "narrative": "You are setting up a school account. The system warns that your chosen password appears in a leaked password database.",
                "interface_type": "password",
                "interface": {
                    "attempt": "student2024",
                    "strength": "Very Weak",
                    "warning": "Found in 14,000 known breaches — crack time: instant",
                },
                "choices": [
                    _choice(
                        "keep",
                        "Keep student2024 because it is easy to remember",
                        "An attacker cracked your account in seconds using a dictionary attack.",
                        "Common patterns and breach-listed passwords fail immediately against modern attacks.",
                        0,
                    ),
                    _choice(
                        "strong",
                        "Create a unique passphrase with MFA enabled",
                        "Your account resisted automated guessing and credential stuffing.",
                        "Long unique passphrases plus MFA dramatically improve account security.",
                        100,
                        is_best=True,
                    ),
                    _choice(
                        "tweak",
                        "Change it slightly to student2024!",
                        "Adding one symbol to a known weak password still cracks quickly.",
                        "Simple tweaks to weak passwords remain vulnerable to smart guessing.",
                        25,
                    ),
                ],
            },
        ],
        "quiz": [
            {
                "question": "Which password is strongest?",
                "options": ["password123", "student2024", "River!Cloud9-Mirror-Study", "12345678"],
                "correct": 2,
                "explanation": "Long passphrases with mixed characters and no common patterns resist guessing best.",
            },
            {
                "question": "Why is password reuse dangerous?",
                "options": ["It makes typing faster", "One breach can unlock many accounts", "It improves MFA", "It encrypts your files"],
                "correct": 1,
                "explanation": "Attackers try stolen credentials across many services—a technique called credential stuffing.",
            },
        ],
    },
}


def get_all_attacks() -> list[dict[str, Any]]:
    return list(ATTACKS.values())


def get_attack(attack_id: str) -> dict[str, Any] | None:
    return ATTACKS.get(attack_id)


def list_attack_summaries() -> list[dict[str, Any]]:
    return [
        {
            "id": attack["id"],
            "name": attack["name"],
            "icon": attack["icon"],
            "difficulty": attack["difficulty"],
            "short_description": attack["short_description"],
            "step_count": len(attack["steps"]),
            "quiz_count": len(attack["quiz"]),
        }
        for attack in ATTACKS.values()
    ]
