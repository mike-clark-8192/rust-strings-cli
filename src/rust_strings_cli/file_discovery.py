"""File discovery module for finding files using glob patterns."""

import glob
import os
from pathlib import Path
from typing import List


def find_files(patterns: List[str]) -> List[Path]:
    """
    Find files matching the given glob patterns.
    
    Args:
        patterns: List of glob patterns to match files against
        
    Returns:
        Sorted list of absolute paths to matching files
    """
    all_files = set()
    
    for pattern in patterns:
        # Use glob with recursive=True for ** patterns
        matched_files = glob.glob(pattern, recursive=True)
        
        for file_path in matched_files:
            path = Path(file_path).resolve()
            
            # Skip directories
            if path.is_dir():
                continue
                
            all_files.add(path)
    
    return sorted(all_files)

