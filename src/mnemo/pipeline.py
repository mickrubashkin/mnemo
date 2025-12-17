from datetime import datetime
from pathlib import Path

from mnemo.enums import Language, Source
from mnemo.sources import SOURCES, export_notes
from mnemo.utils.config import load_config, save_config
from mnemo.utils.storage import load_pickle, save_pickle, find_project_root
from mnemo.utils.text import prepare_for_index
from mnemo.indexer import build_index, search_index



def export_all_notes(sources: set[Source]) -> list:
    all_notes = []

    for source in sources:
        notes = export_notes(source)

        for note in notes:
            note["source"] = source.value

        all_notes.extend(notes)

    return all_notes



def process_notes(notes: list, languages: set[Language]) -> list:
    processed = []

    for note in notes:
        tokens = prepare_for_index(
            note["title"] + " " + note["body"],
            languages=languages
        )
        processed.append({
            "id": note["id"],
            "source": note["source"],
            "title": note["title"],
            "body": note["body"],
            "created": datetime.strptime(note["created"], "%Y-%m-%d %H:%M:%S"),
            "modified": datetime.strptime(note["modified"], "%Y-%m-%d %H:%M:%S"),
            "tokens": tokens
        })

    return processed



def rebuild_index(progress=None) -> None:
    project_root = find_project_root()
    config = load_config(project_root)
    mnemo_dir = project_root / ".mnemo"
    data_dir = mnemo_dir / "data"

    if not mnemo_dir.exists():
        raise RuntimeError(
            "mnemo project is not initialized. "
            "Run `mnemo init` first."
        )

    if progress:
        progress("export:start")

    notes = export_all_notes(config["sources"])

    if progress:
        progress("export:done")

    if progress:
        progress("process:start")

    processed_notes = process_notes(notes, config["languages"])

    if progress:
        progress("process:done")

    if progress:
        progress("index:start")

    index = build_index(processed_notes)

    if progress:
        progress("index:done")

    save_pickle(processed_notes, data_dir / "notes.pkl")
    save_pickle(index, data_dir / "index.pkl")

    # save_config will update last_indexed_at
    save_config(
        project_root,
        sources=config["sources"],
        languages=config["languages"]
    )



def search_notes(query: str):
    project_root = find_project_root()
    config = load_config(project_root)
    data_dir = project_root / ".mnemo" / "data"

    index = load_pickle(data_dir / "index.pkl")
    notes = load_pickle(data_dir / "notes.pkl")
    notes_by_id = {note["id"]: note for note in notes}

    results = search_index(
        query=query,
        index=index,
        notes=notes_by_id,
        languages=config["languages"]
        )

    save_pickle(results, data_dir / "last_search.pkl")

    return results



def get_last_search() -> list:
    project_root = find_project_root()
    path = project_root / ".mnemo" / "data" / "last_search.pkl"

    if not path.exists():
        return []

    return load_pickle(path)




def get_stats():
    project_root = find_project_root()
    config = load_config(project_root)
    data_dir = project_root / ".mnemo" / "data"
    notes = load_pickle(data_dir / "notes.pkl")
    index = load_pickle(data_dir / "index.pkl")

    stats = {
        "project_root": project_root,
        "sources": sorted(s.value for s in config["sources"]),
        "languages": sorted(l.value for l in config["languages"]),
        "created_at": config["created_at"],
        "last_indexed_at": config["last_indexed_at"],
        "notes_count": len(notes),
        "unique_tokens": len(index),
    }

    return stats



def get_notes():
    project_root = find_project_root()
    data_dir = project_root / ".mnemo" / "data"
    notes = load_pickle(data_dir / "notes.pkl")

    return notes



def init_mnemo(sources: set[Source], languages: set[Language], *, progress=None) -> None:
    mnemo_dir = Path.cwd() / ".mnemo"

    if mnemo_dir.exists():
        raise RuntimeError(
            "mnemo project already initialized. "
            "Use `mnemo rebuild` or delete .mnemo directory."
        )

    mnemo_dir.mkdir()
    data_dir = mnemo_dir / "data"
    data_dir.mkdir()

    save_config(
        Path.cwd(),
        sources=sources,
        languages=languages,
    )

    if progress:
        progress("export:start")

    notes = export_all_notes(sources)

    if progress:
        progress("export:done")

    if progress:
        progress("process:start")

    processed_notes = process_notes(notes, languages)

    if progress:
        progress("process:done")

    if progress:
        progress("index:start")

    index = build_index(processed_notes)

    if progress:
        progress("index:done")

    save_pickle(processed_notes, data_dir / "notes.pkl")
    save_pickle(index, data_dir / "index.pkl")
