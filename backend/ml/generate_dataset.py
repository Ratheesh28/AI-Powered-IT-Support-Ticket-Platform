"""Generate a labelled SYNTHETIC demo dataset of IT support tickets.

!!! THIS IS DEMO DATA !!!
Every row is produced by combining hand-written phrases with a fixed random
seed. It is NOT real company data. Because it is template-based, scores
measured on it will look better than they would on real tickets, so treat the
metrics as a demonstration of the pipeline, not as a production claim.

To make it less trivial, the generator adds:
  * shared "noise" sentences that appear in every category,
  * a few deliberately overlapping tickets (e.g. VPN + password), each
    labelled with its most likely root-cause team,
  * occasional typos.

Run:  python -m ml.generate_dataset
"""
import random
from pathlib import Path

import pandas as pd

SEED = 42
ROWS_PER_CATEGORY = 250
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "tickets_demo.csv"

# category -> (titles, symptom sentences, detail sentences)
CONTENT = {
    "Network": (
        [
            "Wifi keeps disconnecting",
            "Cannot connect to VPN",
            "No internet access in my office",
            "Very slow network speed",
            "Cannot reach shared drive",
            "Intranet site not loading",
            "Ethernet port not working",
            "DNS error on all websites",
            "Video calls lagging badly",
            "Proxy error when browsing",
        ],
        [
            "The wifi drops every few minutes and I have to reconnect manually.",
            "The VPN client connects but then times out after a minute.",
            "I have no internet connection even though the cable is plugged in.",
            "Downloads and web pages are extremely slow compared to yesterday.",
            "I cannot map the network shared drive, it says the network path was not found.",
            "Websites show a DNS server not responding error.",
            "The ethernet port on my desk gives no link light and no connectivity.",
            "Video meetings freeze and audio cuts out because of high latency.",
            "The office wifi network does not appear in the list of available networks.",
            "I get a proxy authentication error whenever I open any external website.",
            "Ping to the internal servers is timing out and packets are being lost.",
            "The firewall seems to be blocking access to the internal portal.",
            "My IP address shows as limited connectivity on the network adapter.",
            "The router on our floor keeps restarting and everyone loses connection.",
            "Remote desktop over VPN is unusably slow from home broadband.",
        ],
        [
            "Other colleagues on the same floor have the same issue.",
            "It works fine on my phone hotspot.",
            "I already restarted the network adapter.",
            "Bandwidth looks very low on the speed test.",
            "The problem is worse in the afternoon.",
        ],
    ),
    "Hardware": (
        [
            "Laptop will not turn on",
            "Screen flickering",
            "Keyboard keys not working",
            "Printer paper jam",
            "Docking station not detected",
            "Monitor shows no signal",
            "Laptop overheating and fan loud",
            "Mouse stopped responding",
            "Battery drains very fast",
            "Headset has no audio",
        ],
        [
            "The laptop does not power on at all even when connected to the charger.",
            "The screen flickers and shows horizontal lines after a few minutes.",
            "Several keys on the keyboard are stuck or do not register.",
            "The office printer has a paper jam and shows a tray error.",
            "The docking station is not detecting the external monitors or the keyboard.",
            "My external monitor says no signal even though the cable is connected.",
            "The fan is very loud and the bottom of the laptop gets extremely hot.",
            "The wireless mouse has stopped moving the cursor, I replaced the battery.",
            "The battery only lasts about thirty minutes and the laptop shuts down suddenly.",
            "The headset microphone is dead and I cannot hear anything through the speakers.",
            "The webcam light is on but the camera shows a black picture.",
            "There is a cracked screen on my laptop after it fell off the desk.",
            "The USB ports do not recognise any devices I plug in.",
            "The hard drive is making a clicking noise and the machine freezes.",
            "The power adapter is damaged and the charging cable is frayed.",
        ],
        [
            "I tried a different power outlet.",
            "The device is about three years old.",
            "It happened right after I moved my desk.",
            "I need a replacement unit if it cannot be repaired.",
            "A spare part from the stockroom might fix it.",
        ],
    ),
    "Software": (
        [
            "Outlook keeps crashing",
            "Excel freezes on large files",
            "Need new software installed",
            "License expired for design tool",
            "Teams update failing",
            "Application error on startup",
            "Windows update stuck",
            "Browser extension not working",
            "VS Code will not launch",
            "ERP application throws an error",
        ],
        [
            "Outlook closes unexpectedly when I open an attachment.",
            "Excel stops responding whenever I open a workbook with many formulas.",
            "Please install the latest version of the data analysis software on my machine.",
            "My software license has expired and the application is in read only mode.",
            "The Teams update fails with an error code and keeps retrying.",
            "The application shows an unhandled exception dialog right after launching.",
            "Windows update has been stuck at thirty percent for hours.",
            "The browser extension needed for the finance portal is not loading.",
            "The code editor does not open after the last update and nothing happens.",
            "The ERP system displays an error when I try to save a purchase order.",
            "After the upgrade my PDF reader shows a missing DLL message.",
            "The antivirus software is blocking an approved application from running.",
            "I need admin approval to install a plugin for the reporting tool.",
            "The installer fails halfway with an error and rolls back.",
            "The program runs very slowly and uses all of the memory after the patch.",
        ],
        [
            "I tried reinstalling it but the same error returns.",
            "It started after the latest patch.",
            "The version number is in the about menu.",
            "I attached a screenshot of the error message.",
            "Other users in my team have not seen this.",
        ],
    ),
    "Account Access": (
        [
            "Need password reset",
            "Account locked out",
            "MFA code not arriving",
            "Need access to SharePoint folder",
            "Permission denied on shared folder",
            "Cannot sign in to email",
            "Password expired",
            "Single sign on failing",
            "Request access to Jira project",
            "Authenticator app on new phone",
        ],
        [
            "I forgot my password and need it reset so I can log in.",
            "My account is locked after too many failed login attempts.",
            "The multi factor authentication code never arrives by text message.",
            "I need permission to view the finance team SharePoint folder.",
            "I get an access denied message when opening the shared project folder.",
            "I cannot sign in to my corporate email, it says the credentials are incorrect.",
            "My password has expired and the reset link does not work.",
            "Single sign on redirects me back to the login page in a loop.",
            "Please grant me access to the Jira project for my new team.",
            "I changed phones and need to re register my authenticator app.",
            "A new joiner in my team needs an account and the standard access groups.",
            "My user profile was disabled after I returned from leave.",
            "I need my role permissions updated so I can approve expense reports.",
            "The security token for my login was revoked and I cannot authenticate.",
            "Please unlock my directory account, I cannot log in to any system.",
        ],
        [
            "My manager can confirm the access request.",
            "I need this before the end of the day.",
            "It worked yesterday without any problem.",
            "My employee ID is on the original request form.",
            "I already tried the self service reset page.",
        ],
    ),
}

# Overlapping tickets: genuinely ambiguous wording, labelled by likely root cause.
AMBIGUOUS = [
    ("Cannot log in over VPN", "VPN connects but my login is rejected with invalid credentials.", "Account Access"),
    ("Teams will not load", "Teams shows a blank screen and then an error after I sign in.", "Software"),
    ("Laptop very slow", "The laptop is extremely slow and the fan runs all the time.", "Hardware"),
    ("Cannot open shared drive", "Access denied when I open the shared drive, I do not have permission.", "Account Access"),
    ("Email not syncing", "Outlook is not syncing new mail and shows disconnected.", "Network"),
    ("Printer not found", "My computer cannot find the office printer on the network.", "Network"),
    ("Software install blocked", "The installer cannot run because the machine is not on the corporate network.", "Network"),
    ("Screen share failing", "Screen sharing in the meeting app fails and the display driver crashes.", "Software"),
]

# Sentences that can appear in ANY category, so they carry no label information.
NOISE = [
    "This is blocking my work.",
    "Please help as soon as possible.",
    "It started this morning.",
    "I am working from the main office today.",
    "I am using a company laptop.",
    "Thanks in advance.",
    "This is not urgent but it is annoying.",
    "My manager asked me to raise this ticket.",
]


def _typo(text: str, rng: random.Random) -> str:
    """Randomly drop one character from one word, like a quick typing slip."""
    words = text.split()
    candidates = [i for i, w in enumerate(words) if len(w) > 4]
    if not candidates:
        return text
    i = rng.choice(candidates)
    j = rng.randrange(1, len(words[i]) - 1)
    words[i] = words[i][:j] + words[i][j + 1:]
    return " ".join(words)


def generate(seed: int = SEED, rows_per_category: int = ROWS_PER_CATEGORY) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for category, (titles, symptoms, details) in CONTENT.items():
        for _ in range(rows_per_category):
            parts = [rng.choice(symptoms)]
            if rng.random() < 0.6:
                parts.append(rng.choice(details))
            if rng.random() < 0.5:
                parts.append(rng.choice(NOISE))
            description = " ".join(parts)
            if rng.random() < 0.08:
                description = _typo(description, rng)
            rows.append({"title": rng.choice(titles), "description": description, "category": category})

    # Ambiguous tickets repeated with different noise so they appear a few times each.
    for title, desc, category in AMBIGUOUS:
        for _ in range(6):
            extra = rng.choice(NOISE)
            rows.append({"title": title, "description": f"{desc} {extra}", "category": category})

    df = pd.DataFrame(rows).sample(frac=1, random_state=seed).reset_index(drop=True)
    df.insert(0, "ticket_id", [f"DEMO-{i:04d}" for i in range(1, len(df) + 1)])
    df["data_source"] = "SYNTHETIC_DEMO"
    return df


def main() -> None:
    df = generate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(df)} SYNTHETIC DEMO tickets to {OUTPUT}")
    print(df["category"].value_counts().to_string())


if __name__ == "__main__":
    main()
