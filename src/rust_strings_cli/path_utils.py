"""Path utilities for handling file path formatting."""

import os
from pathlib import Path


def format_path(path: Path, absolute: bool, cwd: Path) -> str:
    """
    Format a file path as absolute or relative.
    
    Args:
        path: Path to format
        absolute: Whether to return absolute path
        cwd: Current working directory for relative paths
        
    Returns:
        Formatted path string
    """
    if absolute:
        return str(path.absolute())
    
    try:
        # Try to make the path relative to CWD
        relative = path.relative_to(cwd)
        return str(relative)
    except ValueError:
        # Path is not relative to CWD (e.g., different drive on Windows)
        return str(path.absolute())