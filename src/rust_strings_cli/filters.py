"""Filtering module for applying length and regex filters to extracted strings."""

import re
from typing import List, Optional, Tuple


def filter_strings(
    strings: List[Tuple[str, int]],
    max_length: int,
    pattern: Optional[str] = None
) -> List[Tuple[str, int]]:
    """
    Filter strings by maximum length and optional regex pattern.
    
    Args:
        strings: List of (string, offset) tuples to filter
        max_length: Maximum allowed string length
        pattern: Optional regex pattern to match strings against
        
    Returns:
        Filtered list of (string, offset) tuples
        
    Raises:
        re.error: If the regex pattern is invalid
    """
    filtered = []
    
    # Compile regex pattern if provided
    regex = None
    if pattern:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise re.error(f"Invalid filter pattern: {str(e)}")
    
    for string, offset in strings:
        # Filter by maximum length
        if len(string) > max_length:
            continue
            
        # Filter by regex pattern if provided
        if regex and not regex.search(string):
            continue
            
        filtered.append((string, offset))
    
    return filtered