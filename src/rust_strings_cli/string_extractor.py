"""String extraction module interfacing with rust-strings library."""

from pathlib import Path
from typing import List, Tuple

import rust_strings
from rust_strings import StringsException, EncodingNotFoundException # type: ignore


def extract_strings(
    file_path: Path,
    encodings: List[str],
    min_length: int,
    buffer_size: int = 1048576
) -> List[Tuple[str, int]]:
    """
    Extract strings from a binary file using rust-strings.
    
    Args:
        file_path: Path to the file to extract strings from
        encodings: List of encodings to try (e.g., ['ascii', 'utf-8', 'utf-16le'])
        min_length: Minimum string length to extract
        buffer_size: Buffer size for reading the file
        
    Returns:
        List of tuples containing (string, offset) pairs
        
    Raises:
        StringsException: If there's an error extracting strings
        EncodingNotFoundException: If an encoding is not supported
    """
    # Normalize encoding names
    normalized_encodings = [_normalize_encoding(enc) for enc in encodings]
    
    try:
        # rust_strings.strings expects 'encodings' parameter (plural) with a list
        results = rust_strings.strings(
            file_path=str(file_path),
            encodings=normalized_encodings,
            min_length=min_length,
            buffer_size=buffer_size
        )
        
        # rust_strings returns a list of tuples: (string, offset)
        return results
        
    except EncodingNotFoundException as e:
        # Re-raise with more context
        raise EncodingNotFoundException(
            f"Unsupported encoding in {encodings}: {str(e)}"
        )
    except StringsException as e:
        # Re-raise with file context
        raise StringsException(
            f"Error extracting strings from {file_path}: {str(e)}"
        )


def _normalize_encoding(encoding: str) -> str:
    """
    Normalize encoding names to rust-strings format.
    
    Args:
        encoding: Encoding name from CLI
        
    Returns:
        Normalized encoding name for rust-strings
    """
    encoding_lower = encoding.lower()
    
    # Map common variations to rust-strings format
    encoding_map = {
        'ascii': 'ascii',
        'utf8': 'utf-8',
        'utf-8': 'utf-8',
        'utf16le': 'utf-16le',
        'utf16be': 'utf-16be',
        'utf-16be': 'utf-16be',
    }
    
    return encoding_map.get(encoding_lower, encoding_lower)
