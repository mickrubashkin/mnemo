import typer
import questionary
from typing import List

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from pathlib import Path

from mnemo.enums import Language, Source
from mnemo.pipeline import get_stats, init_mnemo, rebuild_index, search_notes


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
            print("[green]:white_check_mark: Exporting notes done[/green]")

        elif event == "process:start":
            spinner_tasks["process"] = progress.add_task(
                "Processing notes...", total=None
            )

        elif event == "process:done":
            progress.remove_task(spinner_tasks["process"])
            print("[green]:white_check_mark:Processing notes done[/green]")

        elif event == "index:start":
            spinner_tasks["index"] = progress.add_task(
                "Indexing notes...", total=None
            )

        elif event == "index:done":
            progress.remove_task(spinner_tasks["index"])
            print("[green]:white_check_mark:Indexing notes done[/green]")

    return on_progress



def print_stats(stats):
    print("-------------------")
    print("[bold green]mnemo project stats[/bold green]")
    print("-------------------")
    print(f"Path: {stats['project_root']}")
    print("")
    print(f"Sources:        {stats['sources']}")
    print(f"Languages:      {stats['languages']}")
    print("")
    print(f"Created:        {stats['created_at']}")
    print(f"Last indexed:   {stats['last_indexed_at']}")
    print("")
    print(f"Notes indexed:  {stats['notes_count']}")
    print(f"Index tokens:   {stats['unique_tokens']}")



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

    print("mnemo revert index successfully built :sparkles:")
    stats = get_stats()
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
        print("mnemo revert index successfully built :sparkles:")
        stats = get_stats()
        print_stats(stats)



@app.command()
def search(query: List[str]):
    """Search notes by query."""
    query_text = " ".join(query)
    results = search_notes(query_text)

    typer.echo(f"Found {len(results)} notes")
    for result in results[:10]:
        note = result["note"]
        score = result["score"]
        typer.echo(f"{score} | {note['title']}")



@app.command()
def stats():
    """Print notes index stats."""
    stats = get_stats()
    print_stats(stats)
