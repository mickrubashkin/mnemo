import os
import typer
import questionary
from pathlib import Path
from mnemo import pipeline
from mnemo.enums import Language, Source
from mnemo.pipeline import init_mnemo, rebuild_index, search_notes


app = typer.Typer(no_args_is_help=True)

@app.callback()
def root():
    """mnemo - work with notes index"""
    pass


@app.command()
def rebuild():
    rebuild_index()


@app.command()
def search(query: str):
    search_notes(query)


@app.command()
def stats():
    stats = pipeline.stats()
    typer.echo("mnemo project")
    typer.echo("-------------")
    typer.echo(f"Path: {stats["project_root"]}")
    typer.echo("")
    typer.echo(f"Sources: {', '.join(stats['sources'])}")
    typer.echo(f"Languages: {', '.join(stats['languages'])}")
    typer.echo("")
    typer.echo(f"Created:       {stats['created_at']}")
    typer.echo(f"Last indexed:  {stats['last_indexex_at']}")
    typer.echo("")
    typer.echo(f"Notes indexed: {stats['notes_count']}")
    typer.echo(f"Index tokens:  {stats['tokens_count']}")


@app.command()
def init():
    # TODO: add check .mnemo
    # .mnemo directory already exists.
    # What do you want to do?
    # (*) Cancel
    # ( ) Rebuild index (keep config)
    # ( ) Re-initialize (overwrite config and index)

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
