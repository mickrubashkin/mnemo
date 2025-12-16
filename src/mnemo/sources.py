import json
import subprocess
from pathlib import Path

from mnemo.enums import Source


def export_apple_notes():
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
    notes = []
    return notes



def export_notes(source: Source) -> list[dict]:
    if source is Source.APPLE:
        return export_apple_notes()
    if source is Source.BEAR:
        return export_bear_notes()

    raise ValueError(f"Unsupported source: {souces}")

SOURCES = {
    'apple': export_apple_notes,
    'bear': export_bear_notes
}
