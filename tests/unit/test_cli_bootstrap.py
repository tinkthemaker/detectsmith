from typer.testing import CliRunner

from detectsmith.cli import app


def test_cli_help_lists_core_commands():
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "lint" in result.output
    assert "test" in result.output
    assert "coverage" in result.output
    assert "docs" in result.output
