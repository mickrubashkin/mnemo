from mnemo_cli.utils.text import prepare_for_search


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



def search_index(*, query: str, index, notes, languages):
    if query == "":
        return []

    # Step 1. Prepare query
    query_tokens = prepare_for_search(query, languages)

    if len(query_tokens) == 0:
        return []

    # Step 2. Search candidates
    note_stats = {}
    max_coverage = 0
    for qt in query_tokens:
        if not qt in index:
            continue

        note_ids = index[qt].keys()
        for note_id in note_ids:
            if note_id not in note_stats:
                note_stats[note_id] = {
                        "matched_tokens": set(),
                        "positions_by_token": {}
                    }

            note_stats[note_id]["matched_tokens"].add(qt)

            if qt not in note_stats[note_id]["positions_by_token"]:
                note_stats[note_id]["positions_by_token"][qt] = []

            note_stats[note_id]["positions_by_token"][qt].extend(index[qt][note_id])

    for note_id, note_stat in note_stats.items():
        coverage = len(note_stat["matched_tokens"])
        note_stat["coverage"] = coverage
        if coverage > max_coverage:
            max_coverage = coverage

    # Step 4. Count frequency
    for note_id, note_stat in note_stats.items():
        frequency = 0
        for _, positions in note_stat["positions_by_token"].items():
            frequency += len(positions)
        note_stat["frequency"] = frequency

    # Step 5. Count phrase_bonus
    for note_stat in note_stats.values():
        note_stat["phrase_matches"] = []
        note_stat["phrase_bonus"] = 0

    if len(query_tokens) >= 2:
        qt_pairs = []
        for i in range(0, len(query_tokens) - 1):
            qt_pairs.append((query_tokens[i], query_tokens[i + 1]))

        # TODO: could be simpler, don't need 3 iner cycles
        for (qt_prev, qt_next) in qt_pairs:
            for note_id, note_stat in note_stats.items():
                if (
                    qt_prev in note_stat["positions_by_token"]
                    and qt_next in note_stat["positions_by_token"]
                    ):
                    prev_positions = note_stat["positions_by_token"][qt_prev]
                    next_positions = note_stat["positions_by_token"][qt_next]
                    for p in prev_positions:
                        if (p + 1) in next_positions:
                            note_stat["phrase_matches"].append({
                                "tokens": (qt_prev, qt_next),
                                "position": p
                            })
                            note_stat["phrase_bonus"] += 1

    # Step 6. Build results
    result = []
    for note_id, note_stat in note_stats.items():
        coverage = note_stat["coverage"]
        frequency = note_stat["frequency"]
        phrase_matches =  note_stat["phrase_matches"]
        phrase_bonus = note_stat["phrase_bonus"]
        matched_tokens = list(filter(lambda qt: qt in note_stat["matched_tokens"], query_tokens))

        item = {
            "note": notes[note_id],
            "score": (coverage, frequency, phrase_bonus),
            "matched_tokens": matched_tokens,
            "phrase_matches": phrase_matches,
            "max_coverage": max_coverage,
        }

        result.append(item)

    # Step 7. Sort results by score (coverage, frequency, phrase bonus)
    result = sorted(
        result,
        key=lambda x: x["score"],
        reverse=True
    )

    return result
