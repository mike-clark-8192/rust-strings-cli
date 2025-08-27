"""Tests for string extractor module."""

from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from rust_strings_cli.string_extractor import extract_strings, _normalize_encoding


class TestNormalizeEncoding:
    """Test the _normalize_encoding function."""
    
    def test_normalize_ascii(self):
        """Test normalizing ASCII encoding."""
        assert _normalize_encoding("ascii") == "ascii"
        assert _normalize_encoding("ASCII") == "ascii"
    
    def test_normalize_utf8(self):
        """Test normalizing UTF-8 encoding."""
        assert _normalize_encoding("utf-8") == "utf-8"
        assert _normalize_encoding("utf8") == "utf-8"
        assert _normalize_encoding("UTF-8") == "utf-8"
        assert _normalize_encoding("UTF8") == "utf-8"
    
    def test_normalize_utf16le(self):
        """Test normalizing UTF-16LE encoding."""
        assert _normalize_encoding("utf-16le") == "utf-16le"
        assert _normalize_encoding("utf16le") == "utf-16le"
        assert _normalize_encoding("UTF-16LE") == "utf-16le"
        assert _normalize_encoding("UTF16LE") == "utf-16le"
    
    def test_normalize_utf16be(self):
        """Test normalizing UTF-16BE encoding."""
        assert _normalize_encoding("utf-16be") == "utf-16be"
        assert _normalize_encoding("utf16be") == "utf-16be"
        assert _normalize_encoding("UTF-16BE") == "utf-16be"
        assert _normalize_encoding("UTF16BE") == "utf-16be"
    
    def test_normalize_unknown(self):
        """Test handling unknown encodings."""
        assert _normalize_encoding("unknown") == "unknown"
        assert _normalize_encoding("latin1") == "latin1"


class TestExtractStrings:
    """Test the extract_strings function."""
    
    @patch('rust_strings_cli.string_extractor.rust_strings.strings')
    def test_extract_strings_basic(self, mock_strings):
        """Test basic string extraction."""
        mock_strings.return_value = [("hello", 0), ("world", 10)]
        
        test_path = Path("/test/file.bin")
        result = extract_strings(test_path, ["ascii"], 5)
        
        assert len(result) == 2
        assert result[0] == ("hello", 0)
        assert result[1] == ("world", 10)
        
        mock_strings.assert_called_once_with(
            file_path=str(test_path),
            encodings=["ascii"],
            min_length=5,
            buffer_size=1048576
        )
    
    @patch('rust_strings_cli.string_extractor.rust_strings.strings')
    def test_extract_strings_multiple_encodings(self, mock_strings):
        """Test extraction with multiple encodings."""
        mock_strings.return_value = [("test", 0)]
        
        test_path = Path("/test/file.bin")
        result = extract_strings(test_path, ["ascii", "utf-8", "utf16le"], 3)
        
        mock_strings.assert_called_once_with(
            file_path=str(test_path),
            encodings=["ascii", "utf-8", "utf-16le"],
            min_length=3,
            buffer_size=1048576
        )
    
    @patch('rust_strings_cli.string_extractor.rust_strings.strings')
    def test_extract_strings_custom_buffer(self, mock_strings):
        """Test extraction with custom buffer size."""
        mock_strings.return_value = []
        
        test_path = Path("/test/file.bin")
        result = extract_strings(test_path, ["ascii"], 5, buffer_size=2048)
        
        mock_strings.assert_called_once_with(
            file_path=str(test_path),
            encodings=["ascii"],
            min_length=5,
            buffer_size=2048
        )
    
    @patch('rust_strings_cli.string_extractor.rust_strings.strings')
    def test_extract_strings_encoding_error(self, mock_strings):
        """Test handling of encoding not found error."""
        from rust_strings import EncodingNotFoundException # type: ignore
        mock_strings.side_effect = EncodingNotFoundException("Unknown encoding")
        
        test_path = Path("/test/file.bin")
        
        with pytest.raises(EncodingNotFoundException) as exc_info:
            extract_strings(test_path, ["invalid"], 5)
        
        assert "Unsupported encoding" in str(exc_info.value)
        assert "['invalid']" in str(exc_info.value)
    
    @patch('rust_strings_cli.string_extractor.rust_strings.strings')
    def test_extract_strings_generic_error(self, mock_strings):
        """Test handling of generic extraction error."""
        from rust_strings import StringsException # type: ignore
        mock_strings.side_effect = StringsException("File not found")
        
        test_path = Path("/test/file.bin")
        
        with pytest.raises(StringsException) as exc_info:
            extract_strings(test_path, ["ascii"], 5)
        
        assert "Error extracting strings from" in str(exc_info.value)
        assert "file.bin" in str(exc_info.value)
    
    @patch('rust_strings_cli.string_extractor.rust_strings.strings')
    def test_extract_strings_normalizes_encodings(self, mock_strings):
        """Test that encodings are normalized before calling rust_strings."""
        mock_strings.return_value = []
        
        test_path = Path("/test/file.bin")
        extract_strings(test_path, ["UTF8", "UTF16LE"], 5)
        
        # Check that encodings were normalized
        mock_strings.assert_called_once()
        call_args = mock_strings.call_args[1]
        assert call_args["encodings"] == ["utf-8", "utf-16le"]
    
    @patch('rust_strings_cli.string_extractor.rust_strings.strings')
    def test_extract_strings_windows_path(self, mock_strings):
        """Test handling of Windows paths."""
        mock_strings.return_value = [("test", 0)]
        
        test_path = Path("C:\\Windows\\System32\\notepad.exe")
        result = extract_strings(test_path, ["ascii"], 5)
        
        mock_strings.assert_called_once()
        call_args = mock_strings.call_args[1]
        assert "notepad.exe" in call_args["file_path"]
