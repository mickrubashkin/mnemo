import subprocess
import json

def run_applescript(path: str):
    result = subprocess.run(
        ["osascript", path],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout.strip()
