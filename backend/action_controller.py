import subprocess
import platform
import re
import difflib


SAFE_COMMANDS = {
    "open settings": {
        "windows": ["cmd", "/c", "start", "ms-settings:"],
        "linux": ["gnome-control-center"],
        "darwin": ["open", "-a", "System Settings"],
    },
    "open chrome": {
        "windows": ["cmd", "/c", "start", "chrome"],
        "linux": ["google-chrome"],
        "darwin": ["open", "-a", "Google Chrome"],
    },
    "sleep computer": {
        "windows": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        "linux": ["systemctl", "suspend"],
        "darwin": ["pmset", "sleepnow"],
    },
}


INTENT_ALIASES = {
    "setting": "open settings",
    "settings": "open settings",
    "open setting": "open settings",
    "open settings": "open settings",
    "open system settings": "open settings",
    "activate sleep mode": "sleep computer",
    "go to sleep mode": "sleep computer",
    "sleep mode": "sleep computer",
}


def get_os() -> str:
    system = platform.system()
    if system == "Windows":
        return "windows"
    if system == "Darwin":
        return "darwin"
    return "linux"


def normalize_command(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    fillers = {"please", "the", "to", "a", "an"}
    words = [w for w in text.split() if w not in fillers]
    cleaned = " ".join(words)

    if cleaned in INTENT_ALIASES:
        return INTENT_ALIASES[cleaned]

    match = difflib.get_close_matches(
        cleaned, SAFE_COMMANDS.keys(), n=1, cutoff=0.75
    )

    return match[0] if match else cleaned


def can_execute(command: str) -> bool:
    return normalize_command(command) in SAFE_COMMANDS


def execute_command(command: str):
    command = normalize_command(command)
    os_name = get_os()
    cmd = SAFE_COMMANDS.get(command, {}).get(os_name)

    if not cmd:
        return False, "Command not supported on this OS."

    try:
        subprocess.Popen(cmd)
        return True, f"Executed: {command}"
    except Exception as exc:
        return False, str(exc)