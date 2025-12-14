import os
import typer
import questionary
from pathlib import Path
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
def init():
    typer.echo("Initialising mnemo")
    default_path = Path(".").resolve()

    try:
        use_default = typer.confirm(
            f"Default dir is '{default_path}' - ok?",
            default=True
        )
    except KeyboardInterrupt:
        typer.echo("\nCancelled.")
        raise typer.Exit(code=0)

    if not use_default:
        try:
            base_path = typer.prompt(
                "Enter directory for mnemo data",
                type=Path
            )
        except KeyboardInterrupt:
            typer.echo("\nCancelled.")
            raise typer.Exit(code=0)
    else:
        base_path = default_path

    if base_path.is_file():
        typer.echo("Provided path points to file, expected a directory.")
        raise typer.Exit(code=1)

    base_path.mkdir(parents=True, exist_ok=True)
    if not (
        os.access(base_path, os.R_OK)
        and os.access(base_path, os.W_OK)
        and os.access(base_path, os.X_OK)
        ):
        typer.echo(f"No read/write access to directory: {base_path}")
        raise typer.Exit(code=1)

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

    init_mnemo(base_path, selected_sources, selected_languages)
