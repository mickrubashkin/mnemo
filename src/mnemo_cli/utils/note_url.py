def build_apple_note_url(note):
    return note["id"]

def build_bear_note_url(note):
    return f"bear://x-callback-url/open-note?id={note['id']}"

def build_note_url(note: dict) -> str:
    source = note["source"]

    if source == "apple":
        return build_apple_note_url(note)

    if source == "bear":
        return build_bear_note_url(note)

    raise ValueError(f"Unsupported note source: {source}")
