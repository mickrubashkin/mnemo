from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from mnemo.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolate_fs(tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        yield


@pytest.fixture
def mock_pipeline():
    with patch("mnemo.cli.init_mnemo") as m_init, \
         patch("mnemo.cli.rebuild_index") as m_rebuild, \
         patch("mnemo.cli.get_stats") as m_stats, \
         patch("mnemo.cli.get_notes") as m_notes, \
         patch("mnemo.cli.search_notes") as m_search, \
         patch("mnemo.cli.get_last_search") as m_last:

        m_stats.return_value = dict(
            notes_count=42,
            sources=["apple"],
            languages=["en"],
            unique_tokens=1_234,
            project_root=Path.cwd(),
        )
        m_notes.return_value = [{"title": "foo"}, {"title": "bar"}]
        m_search.return_value = [
            {"note": {"title": "hit1", "source": "apple", "id": "123"}, "score": 0.9}
        ]
        m_last.return_value = m_search.return_value

        yield Mock(
            init=m_init,
            rebuild=m_rebuild,
            stats=m_stats,
            notes=m_notes,
            search=m_search,
            last=m_last,
        )


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "mnemo - work with notes index" in result.output


def test_init_creates_new_index(mock_pipeline):
    with patch("mnemo.cli.questionary.checkbox") as q_chk:
        q_chk.return_value.ask.side_effect = [["apple"], ["en"]]

        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert mock_pipeline.init.called
        assert "Mnemo index successfully built" in result.output


def test_init_rebuild_if_dir_exists(mock_pipeline):
    Path(".mnemo").mkdir()
    with patch("mnemo.cli.questionary.select") as q_sel:
        q_sel.return_value.ask.return_value = "rebuild"

        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert mock_pipeline.rebuild.called


def test_rebuild_command(mock_pipeline):
    result = runner.invoke(app, ["rebuild"])
    assert result.exit_code == 0
    assert mock_pipeline.rebuild.called
    assert "revert index successfully built" in result.output


def test_search_command(mock_pipeline):
    result = runner.invoke(app, ["search", "foo", "bar"])
    assert result.exit_code == 0
    assert "Found 1 notes" in result.output
    assert "hit1" in result.output


def test_open_apple_note(mock_pipeline):
    with patch("mnemo.cli.subprocess.run") as sub_run:
        result = runner.invoke(app, ["open", "1"])
        assert result.exit_code == 0
        sub_run.assert_called_once()
        assert 'show note id "123"' in sub_run.call_args.args[0][2]


def test_open_bear_note(mock_pipeline):
    mock_pipeline.last.return_value = [
        {"note": {"title": "bear", "source": "bear", "id": "xyz"}}
    ]
    with patch("mnemo.cli.typer.launch") as launch:
        result = runner.invoke(app, ["open", "1"])
        assert result.exit_code == 0
        launch.assert_called_once()


def test_list_command(mock_pipeline):
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "foo" in result.output
    assert "bar" in result.output


def test_stats_command(mock_pipeline):
    result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0
    assert "42 notes" in result.output
