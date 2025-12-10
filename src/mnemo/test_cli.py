from typer.testing import CliRunner

from .cli import app

runner = CliRunner()

def test_cli():
    result = runner.invoke(app, ["Mick", "--city", "Barcelona"])
    assert result.exit_code == 0
    assert "Hello Mick" in result.output
    assert "Let's have a coffee in Barcelona" in result.output
