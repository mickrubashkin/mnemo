import datetime as dt
from pathlib import Path
import re
from unittest.mock import Mock, patch

import pytest

from mnemo import pipeline
from mnemo.enums import Language, Source


@pytest.fixture(autouse=True)
def isolated_fs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture
def fake_notes():
    return [
        {
            "id": "n1",
            "source": "apple",
            "title": "First",
            "body": "Text",
            "created": "2025-01-01 12:00:00",
            "modified": "2025-01-02 12:00:00",
        },
        {
            "id": "n2",
            "source": "bear",
            "title": "Second",
            "body": "More text",
            "created": "2025-01-03 12:00:00",
            "modified": "2025-01-04 12:00:00",
        },
    ]


@pytest.fixture
def mock_deps():
    with patch("mnemo.pipeline.export_notes") as m_export, \
         patch("mnemo.pipeline.build_index") as m_build_idx, \
         patch("mnemo.pipeline.save_pickle") as m_save, \
         patch("mnemo.pipeline.load_pickle") as m_load, \
         patch("mnemo.pipeline.save_config") as m_save_cfg, \
         patch("mnemo.pipeline.load_config") as m_load_cfg, \
         patch("mnemo.pipeline.find_project_root") as m_root:

        m_root.return_value = Path.cwd()
        m_build_idx.return_value = {"fake": "index"}
        m_export.return_value = []

        yield Mock(
            export=m_export,
            build_index=m_build_idx,
            save_pickle=m_save,
            load_pickle=m_load,
            save_config=m_save_cfg,
            load_config=m_load_cfg,
            root=m_root,
        )


def test_export_all_notes(mock_deps):
    mock_deps.export.return_value = [{"id": "a"}]
    notes = pipeline.export_all_notes({Source.APPLE, Source.BEAR})
    assert len(notes) == 2
    assert all(n["source"] in ("apple", "bear") for n in notes)


def test_process_notes(fake_notes):
    processed = pipeline.process_notes(
        fake_notes, languages={Language.EN}
    )
    assert len(processed) == 2
    assert processed[0]["tokens"]
    assert isinstance(processed[0]["created"], dt.datetime)


def test_init_mnemo_creates_dirs_and_calls_pipeline(mock_deps, fake_notes):
    mock_deps.export.return_value = fake_notes
    progress = Mock()

    pipeline.init_mnemo(
        sources={Source.APPLE}, languages={Language.EN}, progress=progress
    )

    assert Path(".mnemo/data").exists()
    assert mock_deps.save_config.called
    assert mock_deps.build_index.called
    assert mock_deps.save_pickle.call_count == 2
    assert progress.call_count == 6


def test_init_mnemo_fails_if_already_exists():
    Path(".mnemo").mkdir()
    with pytest.raises(RuntimeError, match="already initialized"):
        pipeline.init_mnemo({Source.APPLE}, {Language.EN})


def test_rebuild_index_workflow(mock_deps, fake_notes):
    Path(".mnemo").mkdir()
    Path(".mnemo/data").mkdir()
    mock_deps.export.return_value = fake_notes
    progress = Mock()

    pipeline.rebuild_index(progress=progress)

    assert mock_deps.build_index.called
    assert mock_deps.save_pickle.call_count == 2
    assert progress.call_count == 6


def test_rebuild_index_fails_without_mnemo_dir():
    with pytest.raises(RuntimeError, match=re.escape("mnemo project not found (run `mnemo init` first)")):
        pipeline.rebuild_index()


def test_search_notes(mock_deps):
    Path(".mnemo").mkdir()
    Path(".mnemo/data").mkdir()
    fake_index = {"token": {"n1": [0]}}
    fake_notes = [{"id": "n1", "title": "Hit"}]
    mock_deps.load_pickle.side_effect = (
        fake_index,
        fake_notes,
    )
    with patch("mnemo.pipeline.search_index") as m_search:
        m_search.return_value = [{"note": {"id": "n1"}, "score": 0.9}]
        results = pipeline.search_notes("query")

    assert len(results) == 1
    assert results[0]["note"]["id"] == "n1"
    m_search.assert_called_once()


def test_get_last_search_empty_if_no_file():
    with patch("mnemo.pipeline.find_project_root", return_value=Path.cwd()):
        assert pipeline.get_last_search() == []



def test_get_stats(mock_deps):
    Path(".mnemo").mkdir()
    Path(".mnemo/data").mkdir()
    fake_cfg = {
        "sources": {Source.APPLE},
        "languages": {Language.EN},
        "created_at": "2025-01-01",
        "last_indexed_at": "2025-01-02",
    }
    fake_notes = [{"id": "n1"}, {"id": "n2"}]
    fake_index = {"token1": 1, "token2": 2}
    mock_deps.load_config.return_value = fake_cfg
    mock_deps.load_pickle.side_effect = (fake_notes, fake_index)

    stats = pipeline.get_stats()

    assert stats["notes_count"] == 2
    assert stats["unique_tokens"] == 2
    assert stats["sources"] == ["apple"]
    assert stats["languages"] == ["en"]


def test_get_notes(mock_deps):
    Path(".mnemo").mkdir()
    Path(".mnemo/data").mkdir()
    fake_notes = [{"id": "n1"}]
    mock_deps.load_pickle.return_value = fake_notes
    assert pipeline.get_notes() == fake_notes
