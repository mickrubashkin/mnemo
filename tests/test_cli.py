from typer.testing import CliRunner

from mnemo.cli import app

runner = CliRunner()

def test_cli():
    result = runner.invoke(app, ["Mick"])
    assert result.exit_code == 0
    assert "Hello Mick" in result.output
