import subprocess
import typer
import questionary
from typing import List

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from pathlib import Path

from mnemo.enums import Language, Source
from mnemo.pipeline import get_last_search, get_notes, get_stats, init_mnemo, rebuild_index, search_notes
from mnemo.sources import open_note
from mnemo.utils.note_url import build_note_url
from mnemo.utils.storage import load_pickle


app = typer.Typer(no_args_is_help=True)

@app.callback()
def root():
    """
    mnemo - work with notes index
    """
    pass


def make_progress_handler(progress: Progress):
    spinner_tasks = {}

    def on_progress(event: str):
        if event == "export:start":
            spinner_tasks["export"] = progress.add_task(
                "Exporting notes...", total=None
            )

        elif event == "export:done":
            progress.remove_task(spinner_tasks["export"])
            print(":sparkles: [green]Exporting notes done[/green]")

        elif event == "process:start":
            spinner_tasks["process"] = progress.add_task(
                "Processing notes...", total=None
            )

        elif event == "process:done":
            progress.remove_task(spinner_tasks["process"])
            print(":sparkles: [green]Processing notes done[/green]")

        elif event == "index:start":
            spinner_tasks["index"] = progress.add_task(
                "Indexing notes...", total=None
            )

        elif event == "index:done":
            progress.remove_task(spinner_tasks["index"])
            print(":sparkles: [green]Indexing notes done[/green]")

    return on_progress



def print_stats(stats):
    print("[bold underline green]Project Stats[/bold underline green]\n")
    print(f"Indexed         {stats['notes_count']} notes")
    print(f"Note sources    {stats['sources']}")
    print(f"Note languages  {stats['languages']}")
    print(f"Unique tokens   {stats['unique_tokens']}")
    print(f"Project path    {stats['project_root']}")


@app.command()
def init():
    """
    Initialize project
    """
    project_root = Path.cwd()
    mnemo_dir = project_root / ".mnemo"

    action = None
    if mnemo_dir.exists():
        action = questionary.select(
            ".mnemo directory already exists. What do you want to do?",
            choices=[
                questionary.Choice("Cancel", value="cancel"),
                questionary.Choice("Rebuild index (keep config)", value="rebuild"),
                questionary.Choice("Re-initialize (overwrite config and index)", value="reinit"),
            ],
        ).ask()

    if action is None or action == "cancel":
        typer.echo("Cancelled.")
        raise typer.Exit(code=0)
    if action == "rebuild":
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            transient=True,
        ) as progress:

            on_progress = make_progress_handler(progress)
            rebuild_index(progress=on_progress)
            print(":party_popper: [green]Revert index successfully built[/green] :party_popper:")
            stats = get_stats()
            print_stats(stats)
            raise typer.Exit(code=0)
    if action == "reinit":
        import shutil
        shutil.rmtree(mnemo_dir)

    print("Initialising mnemo")

    source_choices = []
    for src in Source:
        checked = src == Source.APPLE
        source_choices.append(
            questionary.Choice(src.value, checked=checked)
        )
    note_sources = questionary.checkbox(
        "Select notes sources to index:",
        choices=source_choices,
    ).ask()

    if note_sources is None:
        print("Cancelled.")
        raise typer.Exit(code=0)
    if not note_sources:
        print("Select at least one note source.")
        raise typer.Exit(code=1)

    language_choices = []
    for lang in Language:
        checked = lang == Language.EN
        choice = questionary.Choice(lang.value, checked=checked)
        language_choices.append(choice)

    note_languages = questionary.checkbox(
        "Select your note languages:",
        choices=language_choices,
    ).ask()

    if note_languages is None:
        print("Cancelled.")
        raise typer.Exit(code=0)
    if not note_languages:
        print("Select at least one note language.")
        raise typer.Exit(code=1)

    selected_sources = {Source(code) for code in note_sources}
    selected_languages = {Language(code) for code in note_languages}

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        transient=True,
    ) as progress:

        on_progress = make_progress_handler(progress)
        init_mnemo(selected_sources, selected_languages, progress=on_progress)

    print(":sparkles: [green]Mnemo revert index successfully built[/green]")
    stats = get_stats()
    print("")
    print_stats(stats)



@app.command()
def rebuild():
    """
    Rebuild search index using existing mnemo configuration.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        transient=True,
    ) as progress:

        on_progress = make_progress_handler(progress)
        rebuild_index(progress=on_progress)
        print(":sparkles: [green]Mnemo revert index successfully built[/green]")
        stats = get_stats()
        print("")
        print_stats(stats)



@app.command()
def search(query: List[str]):
    """Search notes by query."""
    query_text = " ".join(query)
    results = search_notes(query_text)

    print(f"Found {len(results)} notes (show top 10)")
    for i, result in enumerate(results[:10], 1):
        note = result["note"]
        score = result["score"]
        source = note["source"]

        print(f"{i}. {note['title']} | {score}")
        print(f"[dim]{source} note -> mnemo open {i}[/dim]")



@app.command()
def open(index: int):
    """
    Open note from the last search
    """
    results = get_last_search()
    if index < 1 or index > len(results):
        print("Invalid index.")
        raise typer.Exit(code=1)
    note = results[index - 1]["note"]
    if note["source"] == "apple":
        note_id = note["id"]
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
    if note["source"] == "bear":
        url = build_note_url(note)
        typer.launch(url)



@app.command()
def list():
    """
    Print all notes title
    """
    # TODO: think about cap, sort options (by date, by title, ascending, descedning etc)
    notes = get_notes()
    titles = [n["title"] for n in notes]
    for t in titles:
        print(t)

@app.command()
def stats():
    """Print notes index stats."""
    stats = get_stats()
    print_stats(stats)
