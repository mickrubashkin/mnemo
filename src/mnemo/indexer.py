def build_index(notes):
    index = {}

    for note in notes:
        note_id = note["id"]
        tokens = note["tokens"]

        for (token, pos) in tokens:
            if token not in index:
                index[token] = {}
            if note_id not in index[token]:
                index[token][note_id] = []
                index[token][note_id].append(pos)
            else:
                index[token][note_id].append(pos)

    return index


def search_index(*, query, index, notes, languages):
    # TODO: implement search index

    return "TBD"
