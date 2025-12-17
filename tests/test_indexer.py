from unittest.mock import patch

import pytest

from mnemo import indexer
from mnemo.enums import Language


@pytest.fixture
def notes():
    return [
        {
            "id": "n1",
            "title": "First note",
            "body": "Python ai",
            "tokens": [("python", 0), ("ai", 1)],
        },
        {
            "id": "n2",
            "title": "Second note",
            "body": "Python with data",
            "tokens": [("python", 0), ("data", 2)],
        },
    ]


def test_build_index(notes):
    idx = indexer.build_index(notes)
    assert "python" in idx
    assert "ai" in idx
    assert "data" in idx
    assert idx["python"]["n1"] == [0]
    assert idx["python"]["n2"] == [0]


@patch("mnemo.indexer.prepare_for_search")
def test_search_index_empty_query(prep):
    prep.return_value = []
    res = indexer.search_index(
        query="", index={}, notes={}, languages={Language.EN}
    )
    assert res == []


@patch("mnemo.indexer.prepare_for_search")
def test_search_index_no_match(prep):
    prep.return_value = ["rust"]
    res = indexer.search_index(
        query="rust", index={"python": {}}, notes={}, languages={Language.EN}
    )
    assert res == []


@patch("mnemo.indexer.prepare_for_search")
def test_search_index_single_token(prep, notes):
    idx = indexer.build_index(notes)
    prep.return_value = ["python"]
    res = indexer.search_index(
        query="python", index=idx, notes={n["id"]: n for n in notes}, languages={Language.EN}
    )
    assert len(res) == 2
    assert res[0]["note"]["id"] in ("n1", "n2")
    assert all("python" in r["matched_tokens"] for r in res)


@patch("mnemo.indexer.prepare_for_search")
def test_search_index_phrase_bonus(prep, notes):
    idx = indexer.build_index(notes)
    prep.return_value = ["python", "ai"]
    res = indexer.search_index(
        query="python ai", index=idx, notes={n["id"]: n for n in notes}, languages={Language.EN}
    )
    n1 = next(r for r in res if r["note"]["id"] == "n1")
    n2 = next(r for r in res if r["note"]["id"] == "n2")
    assert n1["phrase_matches"]
    assert not n2["phrase_matches"]
    assert n1["score"] > n2["score"]
