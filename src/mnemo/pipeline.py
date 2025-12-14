from datetime import datetime
from pathlib import Path

from mnemo.enums import Language, Source
from mnemo.sources import SOURCES
from mnemo.utils.storage import load_pickle, save_pickle
from mnemo.utils.text import normalize_text
from mnemo.indexer import build_index, search_index


def export_all_notes(sources) -> list:
    if sources is None:
        sources = list(SOURCES.keys())

    all_notes = []
    for source_name in sources:
        exporter = SOURCES[source_name]
        notes = exporter()

        for note in notes:
            note['source'] = source_name
            note['id'] = f"{source_name}_{note['id']}"

        all_notes.extend(notes)

    return all_notes


def process_notes(notes: list) -> list:
    processed = []

    for note in notes:
        normalized_text = normalize_text(note['title'] + ' ' + note['body'])
        processed.append({
            'id': note['id'],
            'source': note['source'],
            'title': note['title'],
            'body': note['body'],
            'created': datetime.strptime(note['created'], '%Y-%m-%d %H:%M:%S'),
            'modified': datetime.strptime(note['modified'], '%Y-%m-%d %H:%M:%S'),
            'normalized_text': normalized_text
        })

    return processed


def rebuild_index():
    # TODO: use sources, remove hardcoded values
    notes = export_all_notes(['apple', 'bear'])
    processed_notes = process_notes(notes)

    # TODO: fix hardcoded pathes
    save_pickle(processed_notes, './data/notes.pkl')
    index = build_index(processed_notes)
    save_pickle(index, './data/index.pkl')


def search_notes(query: str):
    index = load_pickle('./data/index.pkl')
    notes = load_pickle('./data/notes.pkl')

    results = search_index(query, index, notes)
    return results

def init_mnemo(base_path: Path, sources: set[Source], languages: set[Language]) -> None:
    data_dir = base_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    notes = export_all_notes(sources)

    processed_notes = process_notes(notes)
    save_pickle(processed_notes, data_dir / "notes.pkl")

    index = build_index(processed_notes)
    save_pickle(index, data_dir / "index.pkl")
