"""Tests for path utilities module."""

import os
from pathlib import Path
import pytest

from rust_strings_cli.path_utils import format_path


class TestFormatPath:
    """Test the format_path function."""
    
    def test_format_absolute_path(self, tmp_path):
        """Test formatting as absolute path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        result = format_path(test_file, absolute=True, cwd=tmp_path)
        assert Path(result).is_absolute()
        assert result == str(test_file.absolute())
    
    def test_format_relative_path_same_dir(self, tmp_path):
        """Test formatting relative path in same directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        result = format_path(test_file, absolute=False, cwd=tmp_path)
        assert result == "test.txt"
    
    def test_format_relative_path_subdirectory(self, tmp_path):
        """Test formatting relative path in subdirectory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.txt"
        test_file.write_text("content")
        
        result = format_path(test_file, absolute=False, cwd=tmp_path)
        assert result == str(Path("subdir") / "test.txt")
    
    def test_format_relative_path_parent_directory(self, tmp_path):
        """Test formatting path in parent directory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # When cwd is subdir and file is in parent
        result = format_path(test_file, absolute=False, cwd=subdir)
        # Should return absolute path since it can't be made relative
        assert Path(result).is_absolute()
        assert result == str(test_file.absolute())
    
    def test_format_path_different_drive_windows(self, tmp_path):
        """Test handling paths on different drives (Windows-specific behavior)."""
        # This test simulates the behavior but works on all platforms
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Simulate a different root by using a path that can't be relative
        fake_cwd = Path("/completely/different/root")
        
        result = format_path(test_file, absolute=False, cwd=fake_cwd)
        # Should return absolute path when can't make relative
        assert Path(result).is_absolute()
    
    def test_format_path_preserves_path_type(self, tmp_path):
        """Test that the function returns a string."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        result_abs = format_path(test_file, absolute=True, cwd=tmp_path)
        result_rel = format_path(test_file, absolute=False, cwd=tmp_path)
        
        assert isinstance(result_abs, str)
        assert isinstance(result_rel, str)
    
    def test_format_path_handles_dots(self, tmp_path):
        """Test handling paths with dots."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / ".." / "test.txt"
        test_file = test_file.resolve()
        test_file.write_text("content")
        
        result = format_path(test_file, absolute=False, cwd=tmp_path)
        assert result == "test.txt"
    
    def test_format_path_nested_structure(self, tmp_path):
        """Test with deeply nested directory structure."""
        deep_dir = tmp_path / "a" / "b" / "c"
        deep_dir.mkdir(parents=True)
        test_file = deep_dir / "test.txt"
        test_file.write_text("content")
        
        result = format_path(test_file, absolute=False, cwd=tmp_path)
        assert result == str(Path("a") / "b" / "c" / "test.txt")
    
    def test_format_path_with_symlinks(self, tmp_path):
        """Test handling of symbolic links."""
        if os.name == 'nt':
            pytest.skip("Symlink test requires admin privileges on Windows")
        
        real_file = tmp_path / "real.txt"
        real_file.write_text("content")
        link_file = tmp_path / "link.txt"
        link_file.symlink_to(real_file)
        
        # Format the symlink path
        result = format_path(link_file, absolute=False, cwd=tmp_path)
        # The resolved path should be used
        assert "link.txt" in result or "real.txt" in result