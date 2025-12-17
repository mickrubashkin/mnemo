from datetime import datetime, timedelta
import json
import os
import sqlite3
import subprocess
from pathlib import Path

from mnemo.enums import Source



def open_apple_note(note_id: str) -> None:
    script = f'''
    tell application "Notes"
        activate
        show note id "{note_id}"
    end tell
    '''
    subprocess.run(
        ["osascript", "-e", script],
        check=False
    )



def open_note(note: dict) -> None:
    source = note["source"]
    if source == "apple":
        open_apple_note(note["id"])
        return
    if source == "bear":
        # url = build_note_url(note)
        # typer.launch(url)
        # return
        pass


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
    db_path = os.path.expanduser(
        '~/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite'
    )

    if not os.path.exists(db_path):
        print("Ber db not found")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ZUNIQUEIDENTIFIER, ZTITLE, ZTEXT, ZCREATIONDATE, ZMODIFICATIONDATE
        FROM ZSFNOTE
        WHERE ZTRASHED = 0
        ORDER BY ZMODIFICATIONDATE DESC
    """)

    bear_notes = cursor.fetchall()
    conn.close()

    notes = []
    for note in bear_notes:
        uid, title, body, created_timestamp, modified_timestamp = note
        created = datetime(2001, 1, 1) + timedelta(seconds=created_timestamp)
        created_string = created.strftime("%Y-%m-%d %H:%M:%S")
        modified = datetime(2001, 1, 1) + timedelta(seconds=modified_timestamp)
        modified_string = modified.strftime("%Y-%m-%d %H:%M:%S")

        notes.append({
            "id": uid,
            "title": title,
            "body": body,
            "created": created_string,
            "modified": modified_string
        })

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
