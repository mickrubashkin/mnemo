import json
import subprocess
from pathlib import Path


def export_apple_notes():
    print("Running apple notes export...")
    script_path = (
        Path(__file__).resolve()
        .parent
        / "apple_scripts"
        / "get_notes.scpt"
    )

    result = subprocess.run(
        ['osascript', str(script_path)],
        capture_output=True,
        text=True,
        timeout=300,
        check=True,
    )

    if result.returncode != 0:
        raise Exception(f"AppleScript error: {result.stderr}")

    notes = json.loads(result.stdout)

    return notes

def export_bear_notes():
    pass

SOURCES = {
    'apple': export_apple_notes,
    'bear': export_bear_notes
}
