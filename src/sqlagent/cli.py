"""Typer CLI. M0 provides the command surface; each command is filled in by its milestone."""

from __future__ import annotations

from typing import Annotated, NoReturn

import typer

from sqlagent import __version__
from sqlagent.config import load_settings

app = typer.Typer(
    name="sqlagent",
    help="Guarded Text-to-SQL agent over AdventureWorks on PostgreSQL.",
    no_args_is_help=True,
    add_completion=False,
)
db_app = typer.Typer(help="Database setup and checks.", no_args_is_help=True)
index_app = typer.Typer(help="Build schema, value and example indexes.", no_args_is_help=True)
bird_app = typer.Typer(help="Phase 2: BIRD Mini-Dev (PostgreSQL) benchmark.", no_args_is_help=True)
mcp_app = typer.Typer(help="MCP server exposing the guarded engine.", no_args_is_help=True)
app.add_typer(db_app, name="db")
app.add_typer(index_app, name="index")
app.add_typer(bird_app, name="bird")
app.add_typer(mcp_app, name="mcp")

NOT_IMPLEMENTED_EXIT = 2


def _not_implemented(command: str, milestone: str) -> NoReturn:
    typer.echo(f"`sqlagent {command}` is not implemented yet (planned in {milestone}).", err=True)
    raise typer.Exit(code=NOT_IMPLEMENTED_EXIT)


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command("config")
def show_config() -> None:
    """Print the effective configuration (no secrets)."""
    typer.echo(load_settings().model_dump_json(indent=2))


@db_app.command("setup")
def db_setup() -> None:
    """Create read-only roles, grants, RLS policies and the row-count manifest."""
    _not_implemented("db setup", "M1")


@index_app.command("build")
def index_build() -> None:
    """Build Chroma collections for columns, values and examples."""
    _not_implemented("index build", "M3")


@app.command()
def ask(
    question: Annotated[str, typer.Argument(help="Question in plain English.")],
    as_rep: Annotated[int | None, typer.Option(help="Scope to a salesperson ID.")] = None,
    variant: Annotated[str, typer.Option(help="Pipeline variant or 'agent'.")] = "self_correct",
) -> None:
    """Answer a question with guarded SQL."""
    _not_implemented("ask", "M5")


@app.command()
def analyze(
    question: Annotated[str, typer.Argument(help="A 'why' / 'what changed' question.")],
    as_rep: Annotated[int | None, typer.Option(help="Scope to a salesperson ID.")] = None,
) -> None:
    """Run the analyst agent and write a cited findings report."""
    _not_implemented("analyze", "M8")


@app.command("eval")
def evaluate(
    variant: Annotated[str, typer.Option(help="Variant name or 'all'.")] = "all",
    gate: Annotated[bool, typer.Option(help="Run the CI regression gate.")] = False,
    analyst: Annotated[bool, typer.Option(help="Evaluate the analyst agent.")] = False,
) -> None:
    """Evaluate variants on the golden set, attacks and analyst set."""
    _not_implemented("eval", "M6")


@bird_app.command("run")
def bird_run() -> None:
    """Run the BIRD Mini-Dev benchmark."""
    _not_implemented("bird run", "B3")


@mcp_app.command("serve")
def mcp_serve(
    as_rep: Annotated[int | None, typer.Option(help="Fix the server scope to a rep ID.")] = None,
) -> None:
    """Serve the guarded engine over MCP (stdio)."""
    _not_implemented("mcp serve", "M9")


@app.command()
def ui() -> None:
    """Launch the Gradio UI."""
    _not_implemented("ui", "M10")


if __name__ == "__main__":
    app()
