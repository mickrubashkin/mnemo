import typer
from typing import Optional
from typing_extensions import Annotated
import subprocess
import json
from pathlib import Path
import re

from .run_applescript import run_applescript

app = typer.Typer()

@app.command()
def main(name: Optional[str] = "Misha", city: Optional[str] = None):
    # docstring is used in the help text (menemo --help)
    """
    Say hi to NAME, optionally with a --city

    If --city provided, get invitation for a coffee.
    """
    print(f"Hello {name}")
    if city:
        print(f"Let's have a coffee in {city}")


    # get all notes data ({id, title, body})
    raw_json = run_applescript("./apple_scripts/get_notes.scpt")

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print("JSON parse error:", e)
        print("Context:", raw_json[e.pos-40:e.pos+40])
        raise

    Path("./data").mkdir(exist_ok=True)
    Path("./data/notes.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Exported", len(data), "notes.")
