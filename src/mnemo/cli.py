from typing import List
import typer
import questionary
from pathlib import Path
from mnemo.enums import Language, Source
from mnemo.pipeline import get_stats, init_mnemo, rebuild_index, search_notes


app = typer.Typer(no_args_is_help=True)

@app.callback()
def root():
    """mnemo - work with notes index"""
    pass


@app.command()
def rebuild():
    rebuild_index()


@app.command()
def search(query: List[str]):
    query_text = " ".join(query)
    results = search_notes(query_text)

    typer.echo(f"Found {len(results)} notes")
    for result in results[:10]:
        note = result["note"]
        score = result["score"]
        typer.echo(f"{score} | {note['title']}")


@app.command()
def stats():
    stats = get_stats()
    typer.echo("mnemo project")
    typer.echo("-------------")
    typer.echo(f"Path: {stats["project_root"]}")
    typer.echo("")
    typer.echo(f"Sources: {', '.join(stats['sources'])}")
    typer.echo(f"Languages: {', '.join(stats['languages'])}")
    typer.echo("")
    typer.echo(f"Created:       {stats['created_at']}")
    typer.echo(f"Last indexed:  {stats['last_indexed_at']}")
    typer.echo("")
    typer.echo(f"Notes indexed: {stats['notes_count']}")
    typer.echo(f"Index tokens:  {stats['unique_tokens']}")


@app.command()
def init():
    # TODO: add check .mnemo
    # .mnemo directory already exists.
    # What do you want to do?
    # (*) Cancel
    # ( ) Rebuild index (keep config)
    # ( ) Re-initialize (overwrite config and index)
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
        rebuild_index()
        raise typer.Exit(code=0)
    if action == "reinit":
        import shutil
        shutil.rmtree(mnemo_dir)

    typer.echo("Initialising mnemo")

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
        typer.echo("Cancelled.")
        raise typer.Exit(code=0)
    if not note_sources:
        typer.echo("Select at least one note source.")
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
        typer.echo("Cancelled.")
        raise typer.Exit(code=0)
    if not note_languages:
        typer.echo("Select at least one note language.")
        raise typer.Exit(code=1)

    selected_sources = {Source(code) for code in note_sources}
    selected_languages = {Language(code) for code in note_languages}

    init_mnemo(selected_sources, selected_languages)
