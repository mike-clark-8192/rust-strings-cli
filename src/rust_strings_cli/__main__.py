#!/usr/bin/env python3
"""Main entry point for rust-strings CLI."""

import typer
from rich.console import Console

app = typer.Typer(
    name="rust-strings",
    help="Extract strings from binary files",
    add_completion=False,
)
console = Console()


@app.command()
def hello():
    """Hello world command for testing the CLI setup."""
    console.print("[green]Hello from rust-strings CLI![/green]")
    console.print("This is a placeholder implementation.")
    console.print("The full CLI will be implemented according to PLAN.md")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()