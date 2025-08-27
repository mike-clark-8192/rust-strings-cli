"""Output formatting module for different output types."""

import json
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple

from rich.box import ROUNDED, SIMPLE
from rich.console import Console
from rich.table import Table


class OutputType(str, Enum):
    json = "json"
    text = "text"
    table = "table"
    rich_table = "rich-table"


class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format(self, results: Dict[str, List[Tuple[str, int]]]) -> str:
        """
        Format the results for output.
        
        Args:
            results: Dictionary mapping file paths to lists of (string, offset) tuples
            
        Returns:
            Formatted string output
        """
        pass


class TextFormatter(OutputFormatter):
    """Simple text formatter with tab-separated values."""
    
    def format(self, results: Dict[str, List[Tuple[str, int]]]) -> str:
        """Format results as tab-separated text."""
        lines = []
        
        for file_path, strings in results.items():
            for string, offset in strings:
                # Escape special characters in strings
                escaped_string = string.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                lines.append(f"{file_path}\t{offset}\t{escaped_string}")
        
        return '\n'.join(lines)


class JsonFormatter(OutputFormatter):
    """JSON formatter for structured output."""
    
    def format(self, results: Dict[str, List[Tuple[str, int]]]) -> str:
        """Format results as JSON."""
        # Convert Path objects to strings for JSON serialization
        json_data = {}
        for file_path, strings in results.items():
            json_data[str(file_path)] = [[string, offset] for string, offset in strings]
        
        return json.dumps(json_data, indent=2, ensure_ascii=False)


class TableFormatter(OutputFormatter):
    """Table formatter using Rich library with simple box style."""
    
    def format(self, results: Dict[str, List[Tuple[str, int]]]) -> str:
        """Format results as a simple table."""
        console = Console()
        table = Table(box=SIMPLE, safe_box=True)
        
        # Add columns
        table.add_column("File Path", style="cyan")
        table.add_column("Offset", style="yellow", justify="right")
        table.add_column("String", style="green")
        
        # Add rows
        for file_path, strings in results.items():
            for string, offset in strings:
                # Truncate long strings
                display_string = string[:100] + "..." if len(string) > 100 else string
                # Escape special characters for display
                display_string = display_string.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                table.add_row(str(file_path), str(offset), display_string)
        
        # Capture table output as string
        with console.capture() as capture:
            console.print(table)
        
        return capture.get()


class RichTableFormatter(OutputFormatter):
    """Rich table formatter with fancy styling."""
    
    def format(self, results: Dict[str, List[Tuple[str, int]]]) -> str:
        """Format results as a rich table with styling."""
        console = Console()
        table = Table(
            title="Extracted Strings",
            box=ROUNDED,
            safe_box=True,
            show_header=True,
            header_style="bold magenta"
        )
        
        # Add columns with styling
        table.add_column("File Path", style="bold cyan", no_wrap=False)
        table.add_column("Offset", style="yellow", justify="right", width=10)
        table.add_column("String", style="green", no_wrap=False)
        
        # Add rows with alternating colors
        row_count = 0
        for file_path, strings in results.items():
            for string, offset in strings:
                # Truncate very long strings
                display_string = string[:200] + "..." if len(string) > 200 else string
                # Escape special characters for display
                display_string = display_string.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                
                # Add row with alternating style
                style = "dim" if row_count % 2 else None
                table.add_row(str(file_path), str(offset), display_string, style=style)
                row_count += 1
        
        # Add footer with total count
        table.caption = f"[dim]Total: {row_count} strings found[/dim]"
        
        # Capture table output as string
        with console.capture() as capture:
            console.print(table)
        
        return capture.get()


def get_formatter(output_type: OutputType) -> OutputFormatter:
    """
    Get the appropriate formatter based on output type.
    
    Args:
        output_type: Type of output formatter ('text', 'json', 'table', 'rich-table')
        
    Returns:
        OutputFormatter instance
        
    Raises:
        ValueError: If output_type is not recognized
    """
    formatters = {
        'text': TextFormatter,
        'json': JsonFormatter,
        'table': TableFormatter,
        'rich-table': RichTableFormatter,
    }
    
    formatter_class = formatters.get(output_type)
    if not formatter_class:
        raise ValueError(f"Unknown output type: {output_type}")
    
    return formatter_class()
