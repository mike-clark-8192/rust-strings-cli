# Implementation Plan for rust-strings-cli

## Project Overview
The rust-strings-cli project provides a command-line interface for the `rust-strings` library, allowing users to extract strings from binary files with various options for filtering, formatting, and outputting results.

## Core Components

### 1. CLI Structure (`__main__.py`)
The main CLI module using Typer will provide the following functionality:

#### Main Command
```bash
rust-strings [options] [glob] [glob...]
```

#### Command-line Arguments
- **globs** (variadic): File patterns to search (processed via `glob.glob`)
  - Support for patterns like `*.py`, `**/*.exe`, etc.
  - If no globs provided, should show help message

#### Command-line Options
- `-a, --abs-path`: Report absolute paths (default: relative to CWD)
- `-e, --encoding`: Encoding to consider, can be repeated (default: ascii, utf-8)
  - Usage: `-e ascii -e utf-16le` or `--encoding ascii --encoding utf-8`
  - Each use adds one encoding to the list
- `-m, --min`: Minimum string length (default: 3)
- `-M, --max`: Maximum string length (default: 256)
- `-o, --output`: Output file path (UTF-8 encoded)
- `-y, --yes`: Overwrite existing output file
- `-f, --filter`: Regex pattern to filter strings
- `-t, --output-type`: Output format (text/json/table/rich-table, default: text)

## Implementation Modules

### 2. File Discovery Module (`file_discovery.py`)
**Purpose**: Handle file pattern matching and filtering

**Key Functions**:
- `find_files(patterns: List[str]) -> List[Path]`
  - Use `glob.glob` with `recursive=True` for `**` patterns
  - Return sorted list of absolute paths

**Edge Cases**:
- Empty pattern list
- Invalid glob patterns
- No matching files
- Permission errors

### 3. String Extraction Module (`string_extractor.py`)
**Purpose**: Interface with rust-strings library

**Key Functions**:
- `extract_strings(file_path: Path, encodings: List[str], min_length: int, buffer_size: int = 1048576) -> List[Tuple[str, int]]`
  - Call `rust_strings.strings()` with parameter `encoding` (note: singular)
  - Pass encodings list directly to rust_strings
  - Handle `StringsException` and `EncodingNotFoundException`
  - Note: max_length filtering happens in filters.py (not supported by rust_strings)

**Encoding Normalization**:
- Normalize CLI encoding names to rust-strings format:
  - "ascii" → "ascii"
  - "utf8" or "utf-8" → "utf-8"
  - "utf16le" or "utf-16le" → "utf-16le"
  - "utf16be" or "utf-16be" → "utf-16be"

### 4. Filtering Module (`filters.py`)
**Purpose**: Apply length and regex filtering to extracted strings

**Key Functions**:
- `filter_strings(strings: List[Tuple[str, int]], max_length: int, pattern: Optional[str]) -> List[Tuple[str, int]]`
  - Filter by maximum length (post-processing since rust_strings doesn't support it)
  - If pattern provided, compile regex and filter matches
  - Handle invalid regex patterns with user-friendly error messages
  - Return filtered results

### 5. Output Formatting Module (`output_formatter.py`)
**Purpose**: Format results in different output types

**Key Classes/Functions**:

#### `TextFormatter`
- Format: `{path}\t{offset}\t{string}`
- One result per line
- Handle special characters in strings

#### `JsonFormatter`
- Format: `{path: [[string, offset], ...]}`
- Use `json.dumps` with proper escaping
- Ensure valid JSON output

#### `TableFormatter`
- Use Rich library with `safe_box=True`
- Columns: File Path | Offset | String
- Handle long strings with truncation

#### `RichTableFormatter`
- Use Rich library with fancy styling
- Add colors and borders
- Support for terminal width detection

### 6. Path Handling Module (`path_utils.py`)
**Purpose**: Handle path relativization and normalization

**Key Functions**:
- `format_path(path: Path, absolute: bool, cwd: Path) -> str`
  - If `--abs-path`, return absolute path
  - Otherwise, try to make relative to CWD
  - Handle cross-drive paths on Windows
  - Normalize path separators

### 7. Main CLI Integration (`__main__.py` - Complete Implementation)
**Structure**:
```python
@app.command()
def main(
    globs: List[str] = typer.Argument(None),
    abs_path: bool = typer.Option(False, "-a", "--abs-path"),
    encodings: List[str] = typer.Option(
        ["ascii", "utf-8"], "-e", "--encoding",
        help="Encoding to consider (can be repeated)"
    ),
    min_length: int = typer.Option(3, "-m", "--min"),
    max_length: int = typer.Option(256, "-M", "--max"),
    output_file: Optional[Path] = typer.Option(None, "-o", "--output"),
    yes: bool = typer.Option(False, "-y", "--yes"),
    filter_pattern: Optional[str] = typer.Option(None, "-f", "--filter"),
    output_type: str = typer.Option("text", "-t", "--output-type"),
):
    # Implementation logic
    # Note: encodings is now a List[str] with repeated option support
```

## Error Handling Strategy

### User-Friendly Error Messages
1. **No files found**: "No files matching the specified patterns were found."
2. **Invalid regex**: "Invalid filter pattern: {error_message}"
3. **Permission denied**: "Cannot access file: {file_path} (Permission denied)"
4. **Invalid encoding**: "Unsupported encoding: {encoding}. Supported: ascii, utf-8, utf-16le, utf-16be"
5. **Output file exists**: "Output file exists. Use -y/--yes to overwrite."

### Exit Codes
- 0: Success
- 1: General error (invalid arguments, etc.)
- 2: No matching files found
- 3: Permission/access error
- 4: Invalid regex pattern

## Testing Strategy

### Unit Tests (`tests/`)
1. **test_file_discovery.py**
   - Test glob pattern matching
   - Test error handling

2. **test_string_extractor.py**
   - Mock rust_strings.strings calls
   - Test encoding handling
   - Test exception handling (StringsException, EncodingNotFoundException)

3. **test_filters.py**
   - Test max length filtering
   - Test regex filtering
   - Test invalid pattern handling

4. **test_output_formatter.py**
   - Test each output format
   - Test special character handling
   - Test large output handling

5. **test_path_utils.py**
   - Test path relativization
   - Test cross-platform compatibility

### Integration Tests
1. **test_cli_integration.py**
   - Test full command execution
   - Test with sample binary files
   - Test output file writing
   - Test all option combinations

## Performance Considerations

1. **Large File Handling**
   - Use appropriate buffer size (default 1MB)
   - Stream processing where possible
   - Progress indication for large file sets (using Rich)

2. **Memory Efficiency**
   - Process files one at a time
   - Stream output to file for large results
   - Avoid loading all results in memory for JSON output

3. **Parallel Processing** (Future Enhancement)
   - Consider using multiprocessing for multiple files
   - Maintain result ordering

## Dependencies Summary
- **rust-strings**: Core string extraction functionality
- **typer[all]**: CLI framework with Rich support included
- **Python stdlib**: glob, re, json, pathlib
- **Note**: Python 3.9+ required (PDM requires 3.9+ for development)

## Development Workflow

### Phase 1: Core Implementation ✓
- [x] Set up project structure
- [x] Configure pyproject.toml
- [x] Create hello world CLI
- [x] Set up development environment

### Phase 2: Basic Functionality
- [ ] Implement file discovery with glob patterns
- [ ] Integrate rust-strings for string extraction
- [ ] Add basic text output formatting
- [ ] Handle file path formatting (absolute/relative)

### Phase 3: Advanced Features
- [ ] Add regex filtering support
- [ ] Implement all output formats (JSON, tables)
- [ ] Add encoding configuration
- [ ] Implement output file writing

### Phase 4: Polish & Testing
- [ ] Add comprehensive error handling
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add progress indicators for large operations
- [ ] Documentation and help text improvements

### Phase 5: Release Preparation
- [ ] Performance optimization
- [ ] Cross-platform testing (Windows, Linux, macOS)
- [ ] Create example usage documentation
- [ ] Set up CI/CD pipeline
- [ ] Prepare for PyPI publication

## Example Usage Scenarios

```bash
# Basic usage - find strings in Python files
rust-strings "*.py"

# Recursive search with UTF-16 encoding
rust-strings "**/*.exe" -e utf-16le

# Multiple encodings (repeated option)
rust-strings "**/*.exe" -e ascii -e utf-16le -e utf-8

# Filter for URLs and save to JSON
rust-strings "**/*.bin" -f "https?://[^\s]+" -t json -o urls.json

# Rich table output with absolute paths
rust-strings "/usr/bin/*" -a -t rich-table
```

## Notes and Considerations

1. **Cross-platform Compatibility**
   - Handle path separators correctly
   - Test on Windows, Linux, and macOS

2. **Security Considerations**
   - Validate file paths to prevent directory traversal
   - Handle large files without memory exhaustion
   - Sanitize regex patterns

3. **User Experience**
   - Provide helpful error messages
   - Show progress for long-running operations
   - Include examples in help text
   - Support both short and long option formats

4. **Future Enhancements**
   - Parallel processing for multiple files
   - Support for additional encodings
   - Export to CSV format
   - Configuration file support
   - Verbose/quiet modes
   - String deduplication option
