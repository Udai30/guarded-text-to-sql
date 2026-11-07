import pytest
from typer.testing import CliRunner

from sqlagent import __version__
from sqlagent.cli import NOT_IMPLEMENTED_EXIT, app

runner = CliRunner()


def test_help_lists_all_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("db", "index", "ask", "analyze", "eval", "bird", "mcp", "ui"):
        assert cmd in result.output


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["db", "setup"],
        ["index", "build"],
        ["ask", "Top 5 territories by sales"],
        ["analyze", "Why did sales drop?"],
        ["eval"],
        ["bird", "run"],
        ["mcp", "serve"],
        ["ui"],
    ],
)
def test_stubs_exit_not_implemented(args: list[str]) -> None:
    result = runner.invoke(app, args)
    assert result.exit_code == NOT_IMPLEMENTED_EXIT
