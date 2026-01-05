"""CLI for prompt-manager-cli."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from prompt_manager_cli.utils import (
    DEFAULT_TEMPLATE,
    format_iso_timestamp,
    generate_filename,
    get_git_short_hash,
    get_local_timestamp,
    load_template,
    render_template,
    resolve_unique_filepath,
)

app = typer.Typer(
    name="pm",
    help="A CLI tool to create and organize prompt files for code agents.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()

DEFAULT_DIR = ".pm/prompts"


@app.callback()
def callback() -> None:
    """A CLI tool to create and organize prompt files for code agents."""
    pass


@app.command("init")
def init() -> None:
    """Initialize .pm directory with default template."""
    try:
        pm_dir = Path.cwd() / ".pm"
        template_file = pm_dir / "template.md"

        if template_file.exists():
            console.print(f"[yellow]Already exists:[/yellow] {template_file}")
            raise typer.Exit(code=0)

        pm_dir.mkdir(parents=True, exist_ok=True)
        template_file.write_text(DEFAULT_TEMPLATE)
        console.print(f"[green]Created:[/green] {template_file}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command("new")
def new(
    dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help=f"Output directory for the prompt file. Default: {DEFAULT_DIR}",
    ),
    edit: bool = typer.Option(
        False,
        "--edit",
        "-e",
        help="Open the created file in your editor ($VISUAL or $EDITOR).",
    ),
) -> None:
    """Create a new prompt file with a timestamped filename."""
    try:
        # Determine output directory
        output_dir = Path(dir) if dir else Path.cwd() / DEFAULT_DIR

        # Ensure directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get timestamp and git hash
        now = get_local_timestamp()
        git_hash = get_git_short_hash()

        # Generate filename and resolve collisions
        base_filename = generate_filename(now, git_hash)
        filepath = resolve_unique_filepath(output_dir, base_filename)

        # Load template and render content
        template = load_template()
        content = render_template(
            template=template,
            created_at=format_iso_timestamp(now),
            git_hash=git_hash,
            cwd=str(Path.cwd().absolute()),
        )
        filepath.write_text(content)

        # Print success message
        console.print(f"[green]Created:[/green] {filepath}")

        # Open in editor if requested
        if edit:
            editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
            if editor:
                subprocess.run([editor, str(filepath)])

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
