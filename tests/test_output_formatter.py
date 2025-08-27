"""Tests for output formatter module."""

import json

import pytest

from rust_strings_cli.output_formatter import (JsonFormatter, OutputType,
                                               RichTableFormatter,
                                               TableFormatter, TextFormatter,
                                               get_formatter)


class TestTextFormatter:
    """Test the TextFormatter class."""
    
    def test_format_simple(self):
        """Test basic text formatting."""
        formatter = TextFormatter()
        results = {
            "file1.txt": [("hello", 0), ("world", 10)],
            "file2.txt": [("test", 20)],
        }
        
        output = formatter.format(results)
        lines = output.split("\n")
        
        assert len(lines) == 3
        assert "file1.txt\t0\thello" in output
        assert "file1.txt\t10\tworld" in output
        assert "file2.txt\t20\ttest" in output
    
    def test_format_special_characters(self):
        """Test escaping of special characters."""
        formatter = TextFormatter()
        results = {
            "file.txt": [
                ("line1\nline2", 0),
                ("tab\there", 10),
                ("carriage\rreturn", 20),
            ],
        }
        
        output = formatter.format(results)
        
        assert "\\n" in output
        assert "\\t" in output
        assert "\\r" in output
        assert "\n" not in output.split("\t")[2]  # No actual newline in string field
    
    def test_format_empty_results(self):
        """Test formatting empty results."""
        formatter = TextFormatter()
        results = {}
        
        output = formatter.format(results)
        assert output == ""
    
    def test_format_preserves_order(self):
        """Test that order is preserved."""
        formatter = TextFormatter()
        results = {
            "a.txt": [("first", 0)],
            "b.txt": [("second", 10)],
            "c.txt": [("third", 20)],
        }
        
        output = formatter.format(results)
        lines = output.split("\n")
        
        assert "a.txt" in lines[0]
        assert "b.txt" in lines[1]
        assert "c.txt" in lines[2]


class TestJsonFormatter:
    """Test the JsonFormatter class."""
    
    def test_format_valid_json(self):
        """Test that output is valid JSON."""
        formatter = JsonFormatter()
        results = {
            "file1.txt": [("hello", 0), ("world", 10)],
            "file2.txt": [("test", 20)],
        }
        
        output = formatter.format(results)
        parsed = json.loads(output)
        
        assert "file1.txt" in parsed
        assert "file2.txt" in parsed
        assert parsed["file1.txt"] == [["hello", 0], ["world", 10]]
        assert parsed["file2.txt"] == [["test", 20]]
    
    def test_format_unicode(self):
        """Test handling of Unicode characters."""
        formatter = JsonFormatter()
        results = {
            "file.txt": [("hello 世界", 0), ("émoji 😀", 10)],
        }
        
        output = formatter.format(results)
        parsed = json.loads(output)
        
        assert parsed["file.txt"][0][0] == "hello 世界"
        assert parsed["file.txt"][1][0] == "émoji 😀"
    
    def test_format_empty_results(self):
        """Test formatting empty results as JSON."""
        formatter = JsonFormatter()
        results = {}
        
        output = formatter.format(results)
        parsed = json.loads(output)
        
        assert parsed == {}
    
    def test_format_special_characters(self):
        """Test JSON escaping of special characters."""
        formatter = JsonFormatter()
        results = {
            "file.txt": [("quote\"test", 0), ("backslash\\test", 10)],
        }
        
        output = formatter.format(results)
        parsed = json.loads(output)
        
        assert parsed["file.txt"][0][0] == "quote\"test"
        assert parsed["file.txt"][1][0] == "backslash\\test"


class TestTableFormatter:
    """Test the TableFormatter class."""
    
    def test_format_creates_table(self):
        """Test that a table is created."""
        formatter = TableFormatter()
        results = {
            "file.txt": [("hello", 0), ("world", 10)],
        }
        
        output = formatter.format(results)
        
        # Check for table elements
        assert "File Path" in output
        assert "Offset" in output
        assert "String" in output
        assert "file.txt" in output
        assert "hello" in output
        assert "world" in output
    
    def test_format_truncates_long_strings(self):
        """Test truncation of long strings."""
        formatter = TableFormatter()
        long_string = "a" * 150
        results = {
            "file.txt": [(long_string, 0)],
        }
        
        output = formatter.format(results)
        
        assert "..." in output
        assert len(output.split("\n")[0]) < 200  # Reasonable line length
    
    def test_format_escapes_special_chars(self):
        """Test escaping in table output."""
        formatter = TableFormatter()
        results = {
            "file.txt": [("line1\nline2", 0)],
        }
        
        output = formatter.format(results)
        
        assert "\\n" in output


class TestRichTableFormatter:
    """Test the RichTableFormatter class."""
    
    def test_format_creates_rich_table(self):
        """Test that a rich table is created."""
        formatter = RichTableFormatter()
        results = {
            "file.txt": [("hello", 0), ("world", 10)],
        }
        
        output = formatter.format(results)
        
        # Check for rich table elements
        assert "Extracted Strings" in output
        assert "File Path" in output
        assert "Offset" in output
        assert "String" in output
        assert "file.txt" in output
        assert "Total: 2 strings found" in output
    
    def test_format_alternating_rows(self):
        """Test that formatter handles multiple rows."""
        formatter = RichTableFormatter()
        results = {
            "file.txt": [
                ("first", 0),
                ("second", 10),
                ("third", 20),
                ("fourth", 30),
            ],
        }
        
        output = formatter.format(results)
        
        assert "first" in output
        assert "second" in output
        assert "third" in output
        assert "fourth" in output
        assert "Total: 4 strings found" in output



class TestGetFormatter:
    """Test the get_formatter function."""
    

    def test_get_text_formatter(self):
        """Test getting text formatter."""
        formatter = get_formatter(OutputType.text)
        assert isinstance(formatter, TextFormatter)
    
    def test_get_json_formatter(self):
        """Test getting JSON formatter."""
        formatter = get_formatter(OutputType.json)
        assert isinstance(formatter, JsonFormatter)
    
    def test_get_table_formatter(self):
        """Test getting table formatter."""
        formatter = get_formatter(OutputType.table)
        assert isinstance(formatter, TableFormatter)
    
    def test_get_rich_table_formatter(self):
        """Test getting rich table formatter."""
        formatter = get_formatter(OutputType.rich_table)
        assert isinstance(formatter, RichTableFormatter)
    
    def test_get_invalid_formatter(self):
        """Test error on invalid formatter type."""
        with pytest.raises(ValueError) as exc_info:
            get_formatter("invalid") # type: ignore
        
        assert "Unknown output type: invalid" in str(exc_info.value)
