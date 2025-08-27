#!/usr/bin/env python3
"""Main entry point for rust-strings CLI."""

import re
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from .file_discovery import find_files
from .filters import filter_strings
from .output_formatter import get_formatter, OutputType
from .path_utils import format_path
from .string_extractor import extract_strings

# Create Typer app with proper configuration for error handling
app = typer.Typer(
    name="rust-strings",
    help="Extract strings from binary files with various filtering options.",
    add_completion=False,
    no_args_is_help=True,  # Show help when no arguments provided
    pretty_exceptions_show_locals=False,  # Don't show locals in exceptions for security
    pretty_exceptions_short=True,  # Show short tracebacks
    rich_markup_mode="rich",  # Enable rich markup in help
    add_help_option=True,  # Add --help option
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Use stderr for console output to keep stdout clean for actual results
console = Console(stderr=True)


# def validate_output_type(value: str) -> str:
#     """Validate output type parameter."""
#     valid_types = ["text", "json", "table", "rich-table"]
#     if value not in valid_types:
#         raise typer.BadParameter(
#             f"Must be one of: {', '.join(valid_types)}"
#         )
#     return value


def validate_regex(value: Optional[str]) -> Optional[str]:
    """Validate regex pattern parameter."""
    if value is None:
        return None
    try:
        re.compile(value)
        return value
    except re.error as e:
        raise typer.BadParameter(f"Invalid regex pattern: {e}")


@app.command()
def main(
    globs: Annotated[
        List[str],
        typer.Argument(
            help="File search glob patterns (separate multiple with space)",
            metavar="GLOB",
        )
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o",
            help="Output file path (UTF-8 encoded)"
        )
    ] = None,
    encoding: Annotated[
        Optional[List[str]],
        typer.Option(
            "--encoding", "-e", metavar="ENCODING",
            help="Encoding to consider (can be repeated)"
        )
    ] = ["utf-8"],
    min: Annotated[
        int,
        typer.Option(
            "--min", "-m",
            min=1,
            help="Minimum string length"
        )
    ] = 3,
    max: Annotated[
        int,
        typer.Option(
            "--max", "-M",
            min=1,
            help="Maximum string length"
        )
    ] = 256,
    filter: Annotated[
        Optional[str],
        typer.Option(
            "--filter", "-f", metavar="REGEX",
            callback=validate_regex,
            help="Regex pattern to filter strings"
        )
    ] = None,
    output_type: Annotated[
        OutputType,
        typer.Option(
            "--output-type", "-t",
            help="Output format (see docs)",
            case_sensitive=False,
            show_default=True,
        )] = OutputType.text,
    abs_path: Annotated[
        bool,
        typer.Option(
            "--abs-path", "-a",
            help="Report absolute paths instead of relative paths"
        )
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes", "-y",
            help="Overwrite existing output file"
        )
    ] = False,
):
    """
    Extract strings from binary files with various filtering options.
    
    This tool uses the rust-strings library to efficiently extract readable
    strings from binary files. It supports multiple encodings, filtering by
    length and regex patterns, and various output formats.
    """
    
    # Set default encoding if None
    if encoding is None:
        encoding = ["utf-8"]
    
    # Check output file
    if output and output.exists() and not yes:
        raise typer.BadParameter(
            f"Output file exists: {output}. Use -y/--yes to overwrite."
        )
    
    # Get current working directory
    cwd = Path.cwd()
    
    # Find files matching patterns
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Finding files...", total=None)
        
        try:
            files = find_files(globs)
        except Exception as e:
            progress.update(task, completed=True)
            raise typer.BadParameter(f"Error finding files: {e}")
        
        progress.update(task, completed=True)
    
    if not files:
        console.print("[yellow]No files matching the specified patterns were found.[/yellow]")
        raise typer.Exit(2)  # Exit cleanly with no error
    
    console.print(f"[dim]Found {len(files)} file(s) to process[/dim]")
    
    # Process each file and extract strings
    all_results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        for file_path in files:
            task = progress.add_task(
                f"Processing {file_path.name}...",
                total=None
            )
            
            try:
                # Extract strings from file
                strings = extract_strings(
                    file_path=file_path,
                    encodings=encoding,
                    min_length=min
                )
                
                # Apply filters
                strings = filter_strings(strings, max_length=max, pattern=filter)
                
                # Format path
                formatted_path = format_path(file_path, absolute=abs_path, cwd=cwd)
                
                # Store results if any strings found
                if strings:
                    all_results[formatted_path] = strings
                    
            except PermissionError:
                console.print(f"[red]Cannot access file:[/red] {file_path} (Permission denied)")
                progress.update(task, completed=True)
                continue
            except Exception as e:
                console.print(f"[red]Error processing {file_path}:[/red] {e}")
                progress.update(task, completed=True)
                continue
            
            progress.update(task, completed=True)
    
    # Check if we have any results
    if not all_results:
        console.print("[yellow]No strings found in the processed files.[/yellow]")
        raise typer.Exit(0)
    
    # Format output
    try:
        formatter = get_formatter(output_type)
        output_text = formatter.format(all_results)
    except Exception as e:
        raise typer.BadParameter(f"Error formatting output: {e}")
    
    # Write output
    if output:
        try:
            output.write_text(output_text, encoding='utf-8')
            console.print(f"[green]Results written to:[/green] {output}")
        except Exception as e:
            raise typer.BadParameter(f"Error writing output file: {e}")
    else:
        # Print to stdout (not stderr) for pipeable output
        print(output_text)
    
    # Print summary to stderr so it doesn't interfere with piped output
    total_strings = sum(len(strings) for strings in all_results.values())
    console.print(f"[dim]Found {total_strings} strings in {len(all_results)} file(s)[/dim]")


def cli():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli()
