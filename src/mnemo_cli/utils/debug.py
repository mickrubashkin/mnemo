from mnemo_cli.utils.storage import find_project_root, load_pickle


def get_last_search_note() -> dict:
    project_root = find_project_root()
    path = project_root / ".mnemo" / "data" / "last_search.pkl"

    results = load_pickle(path)

    note = results[0]["note"]
    return note

def get_note():
    project_root = find_project_root()
    path = project_root / ".mnemo" / "data" / "notes.pkl"

    results = load_pickle(path)

    note = results[0]
    return note


def debug_show_note():
    note_last_search = get_last_search_note()
    print("Last search note data")
    print(f"keys: {note_last_search.keys()}")
    print("")
    print(f"tokens len: {len(note_last_search["tokens"])}")
    print("")
    # print(note_last_search["tokens"])

    note = get_note()
    print("Saved note data")
    print(f"keys: {note.keys()}")
    print(note)

debug_show_note()
