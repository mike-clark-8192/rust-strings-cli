"""Tests for file discovery module."""

import tempfile
import os
from pathlib import Path
import pytest

from rust_strings_cli.file_discovery import find_files


class TestFindFiles:
    """Test the find_files function."""
    
    def test_find_files_simple_pattern(self, tmp_path):
        """Test finding files with simple glob pattern."""
        # Create test files
        (tmp_path / "test1.txt").write_text("content")
        (tmp_path / "test2.txt").write_text("content")
        (tmp_path / "other.py").write_text("content")
        
        # Change to temp directory for testing
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = find_files(["*.txt"])
            assert len(files) == 2
            assert all(f.suffix == ".txt" for f in files)
        finally:
            os.chdir(original_cwd)
    
    def test_find_files_recursive_pattern(self, tmp_path):
        """Test finding files with recursive glob pattern."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "test.py").write_text("content")
        (subdir / "nested.py").write_text("content")
        
        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = find_files(["**/*.py"])
            assert len(files) == 2
            assert all(f.suffix == ".py" for f in files)
        finally:
            os.chdir(original_cwd)
    
    def test_find_files_multiple_patterns(self, tmp_path):
        """Test finding files with multiple patterns."""
        # Create various files
        (tmp_path / "test.txt").write_text("content")
        (tmp_path / "script.py").write_text("content")
        (tmp_path / "data.json").write_text("content")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = find_files(["*.txt", "*.py"])
            assert len(files) == 2
            assert any(f.suffix == ".txt" for f in files)
            assert any(f.suffix == ".py" for f in files)
        finally:
            os.chdir(original_cwd)
    
    def test_find_files_excludes_directories(self, tmp_path):
        """Test that directories are excluded from results."""
        # Create file and directory
        (tmp_path / "file.txt").write_text("content")
        (tmp_path / "subdir").mkdir()
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = find_files(["*"])
            assert len(files) == 1
            assert files[0].is_file()
        finally:
            os.chdir(original_cwd)
    
    def test_find_files_no_matches(self, tmp_path):
        """Test behavior when no files match the pattern."""
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = find_files(["*.nonexistent"])
            assert files == []
        finally:
            os.chdir(original_cwd)
    
    def test_find_files_returns_absolute_paths(self, tmp_path):
        """Test that returned paths are absolute."""
        (tmp_path / "test.txt").write_text("content")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = find_files(["*.txt"])
            assert all(f.is_absolute() for f in files)
        finally:
            os.chdir(original_cwd)
    
    def test_find_files_sorted_output(self, tmp_path):
        """Test that output is sorted."""
        # Create files in non-alphabetical order
        (tmp_path / "zebra.txt").write_text("content")
        (tmp_path / "apple.txt").write_text("content")
        (tmp_path / "monkey.txt").write_text("content")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = find_files(["*.txt"])
            file_names = [f.name for f in files]
            assert file_names == sorted(file_names)
        finally:
            os.chdir(original_cwd)
