"""Tests for the filters module."""

import re
import pytest

from rust_strings_cli.filters import filter_strings


class TestFilterStrings:
    """Test the filter_strings function."""
    
    def test_filter_by_max_length(self):
        """Test filtering strings by maximum length."""
        strings = [
            ("short", 0),
            ("medium length", 10),
            ("this is a very long string that exceeds the limit", 20),
        ]
        
        filtered = filter_strings(strings, max_length=15)
        assert len(filtered) == 2
        assert all(len(s[0]) <= 15 for s in filtered)
    
    def test_filter_by_regex_pattern(self):
        """Test filtering strings by regex pattern."""
        strings = [
            ("hello world", 0),
            ("test string", 10),
            ("hello python", 20),
            ("goodbye", 30),
        ]
        
        # Filter for strings containing "hello"
        filtered = filter_strings(strings, max_length=100, pattern="hello")
        assert len(filtered) == 2
        assert all("hello" in s[0] for s in filtered)
    
    def test_filter_by_complex_regex(self):
        """Test filtering with complex regex pattern."""
        strings = [
            ("http://example.com", 0),
            ("https://github.com", 10),
            ("ftp://server.com", 20),
            ("not a url", 30),
        ]
        
        # Filter for URLs
        pattern = r"https?://"
        filtered = filter_strings(strings, max_length=100, pattern=pattern)
        assert len(filtered) == 2
        assert all(s[0].startswith("http") for s in filtered)
    
    def test_filter_combined_length_and_pattern(self):
        """Test combining max length and regex filtering."""
        strings = [
            ("test", 0),
            ("test string", 10),
            ("this is a test with a very long description", 20),
            ("no match", 30),
        ]
        
        filtered = filter_strings(strings, max_length=15, pattern="test")
        assert len(filtered) == 2
        assert all("test" in s[0] and len(s[0]) <= 15 for s in filtered)
    
    def test_filter_no_pattern(self):
        """Test filtering with no regex pattern."""
        strings = [
            ("short", 0),
            ("medium", 10),
            ("very very very long string", 20),
        ]
        
        filtered = filter_strings(strings, max_length=10)
        assert len(filtered) == 2
        assert filtered[0][0] == "short"
        assert filtered[1][0] == "medium"
    
    def test_filter_invalid_regex(self):
        """Test handling of invalid regex pattern."""
        strings = [("test", 0)]
        
        with pytest.raises(re.error) as exc_info:
            filter_strings(strings, max_length=100, pattern="[invalid(")
        
        assert "Invalid filter pattern" in str(exc_info.value)
    
    def test_filter_empty_input(self):
        """Test filtering empty list."""
        strings = []
        filtered = filter_strings(strings, max_length=100, pattern="test")
        assert filtered == []
    
    def test_filter_preserves_offsets(self):
        """Test that offsets are preserved during filtering."""
        strings = [
            ("match1", 100),
            ("nomatch", 200),
            ("match2", 300),
        ]
        
        filtered = filter_strings(strings, max_length=100, pattern="match")
        assert len(filtered) == 2
        assert filtered[0][1] == 100
        assert filtered[1][1] == 300
    
    def test_filter_case_sensitive(self):
        """Test that regex filtering is case sensitive by default."""
        strings = [
            ("Hello", 0),
            ("hello", 10),
            ("HELLO", 20),
        ]
        
        filtered = filter_strings(strings, max_length=100, pattern="hello")
        assert len(filtered) == 1
        assert filtered[0][0] == "hello"
    
    def test_filter_special_characters_in_pattern(self):
        """Test filtering with special regex characters."""
        strings = [
            ("test.txt", 0),
            ("test_txt", 10),
            ("test txt", 20),
        ]
        
        # Dot matches any character in regex
        filtered = filter_strings(strings, max_length=100, pattern=r"test\.txt")
        assert len(filtered) == 1
        assert filtered[0][0] == "test.txt"