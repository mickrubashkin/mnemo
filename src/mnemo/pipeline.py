from datetime import datetime
from pathlib import Path

from mnemo.enums import Language, Source
from mnemo.sources import SOURCES
from mnemo.utils.storage import load_pickle, save_pickle, find_project_root
from mnemo.utils.text import prepare_for_index
from mnemo.indexer import build_index, search_index


def export_all_notes(sources: set[Source]) -> list:
    all_notes = []

    for source in sources:
        exporter = SOURCES[source.value]
        notes = exporter()

        for note in notes:
            note['source'] = source.value
            note['id'] = f"{source.value}_{note['id']}"

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


def rebuild_index():
    # TODO: use sources, remove hardcoded values
    # notes = export_all_notes(Source.values())
    # processed_notes = process_notes(notes)

    # # TODO: fix hardcoded pathes
    # save_pickle(processed_notes, './data/notes.pkl')
    # index = build_index(processed_notes)
    # save_pickle(index, './data/index.pkl')
    pass


def search_notes(query: str):
    project_root = find_project_root()
    data_dir = project_root / ".mnemo" / "data"

    index = load_pickle(data_dir / "index.pkl")
    notes = load_pickle(data_dir / "notes.pkl")

    results = search_index(query, index, notes)
    return results

def init_mnemo(sources: set[Source], languages: set[Language]) -> None:
    project_root = Path.cwd()
    mnemo_dir = project_root / ".mnemo"
    data_dir = mnemo_dir / "data"

    data_dir.mkdir(parents=True, exist_ok=True)

    notes = export_all_notes(sources)

    processed_notes = process_notes(notes, languages)
    save_pickle(processed_notes, data_dir / "notes.pkl")

    index = build_index(processed_notes)
    save_pickle(index, data_dir / "index.pkl")
