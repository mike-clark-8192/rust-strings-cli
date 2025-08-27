# Command-line interface for [iddohau/rust-strings](https://github.com/iddohau/rust-strings)

This project provides a CLI for the `rust-strings` library.

Installation: `pip install rust-strings-cli`

## Usage

```bash
rust-strings [options] [glob] [glob...]
```

### Globbing

Globbing is done via [glob.glob](https://docs.python.org/3/library/glob.html#glob.glob). Examples:

```sh
*.py     # all .py files in the CWD
*/*.py   # all .py files that are immediate children of immediate subdirectories of the CWD
**/*.py  # all .py files in the CWD and in subdirectories at any depth
```

### Flags

```
  -a, --abs-path               Always report absolute paths.
                                  Otherwise paths that are children of the CWD
                                  are relativized to the CWD.
  -e, --encodings <encs>       Comma-separated list of encodings to consider while
                                  searching for strings  (default: ascii,utf8)
  -m, --min <length>           Exclude strings shorter than this length (default: 3)
  -M, --max <length>           Exclude strings longer than this length (default: 256)
  -o, --output <file>          Write results to <file>. Output is written as UTF-8.
                                  Without this flag, results are written to stdout.
  -y, --yes                    Overwrite output file if it exists.
  -f, --filter <regex>         Only strings matching this regex will be reported
  -t, --output-type <type>     One of `text`, `json`, `table`, or `rich-table` (default: text)
  -H, --no-hidden              Exclude hidden directories and files (e.g., dotfiles).
```

### Output formats

### Output formats

| Format         | Description                                                                                  |
|----------------|----------------------------------------------------------------------------------------------|
| **text**       | Line-oriented plain text (default). Each result is one line: `{path}\t{offset}\t{string}`    |
| **json**       | One JSON object where keys are file paths, and values are arrays of `[match_string, offset]` |
| **table**      | ASCII table output via [Rich](https://github.com/Textualize/rich) (`safe_box=True`)          |
| **rich-table** | Fancy TUI table output via [Rich](https://github.com/Textualize/rich) tables                 |

---

## Implementation 
### Libraries used
* [Typer](https://github.com/tiangolo/typer) – argument parsing and error reporting  
* [Rich](https://github.com/Textualize/rich) – table formatting  
* Python 3 stdlib: [`glob`](https://docs.python.org/3/library/glob.html), [`re`](https://docs.python.org/3/library/re.html), etc.
###
* Project definition - `pyproject.toml`
* Build - `pdm`
* Build versioning - `pdm`
 ```
[tool.pdm.version]
source = "scm"
```
* Build publishing (PyPI, TestPyPI) - `pdm`

---

## rust-strings Python API Example

```python
# pip install rust-strings

import rust_strings

# Get all ASCII strings from a file with minimum string length
rust_strings.strings(file_path="/bin/ls", min_length=3)
# [('ELF', 1),
#  ('/lib64/ld-linux-x86-64.so.2', 680),
#  ('GNU', 720),
#  ('.<O', 725),
#  ('GNU', 756),
#  ...]

# Control buffer size when reading files (default: 1 MB)
rust_strings.strings(file_path="/bin/ls", min_length=5, buffer_size=1024)

# Specify encoding (default: 'ascii'). Supported: 'ascii', 'utf-8', 'utf-16le', 'utf-16be'
rust_strings.strings(file_path=r"C:\Windows\notepad.exe", min_length=5, encodings=["utf-16le"])

# Multiple encodings are supported
rust_strings.strings(file_path=r"C:\Windows\notepad.exe", min_length=5, encodings=["ascii", "utf-16le"])

# Pass bytes instead of a file path
rust_strings.strings(bytes=b"test\x00\x00", min_length=4, encodings=["ascii"])
# [("test", 0)]

# Write search results to a JSON file
rust_strings.dump_strings("strings.json", bytes=b"test\x00\x00", min_length=4, encodings=["ascii"])
# strings.json content:
# [["test", 0]]
```

---

## License

[MIT](LICENSE)
