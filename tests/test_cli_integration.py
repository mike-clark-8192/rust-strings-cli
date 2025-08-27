"""Integration tests for the rust-strings CLI."""

import json
import os
import tempfile
from pathlib import Path
import subprocess
import sys

import pytest


def run_cli(*args):
    """Helper to run the CLI and capture output."""
    cmd = [sys.executable, "-m", "rust_strings_cli"] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )
    return result


class TestCLIIntegration:
    """Integration tests for the CLI."""
    
    def test_cli_no_args(self):
        """Test CLI with no arguments shows error."""
        result = run_cli()
        assert result.returncode == 0
        assert "Missing argument 'GLOB'" in result.stderr
    
    def test_cli_help(self):
        """Test help output."""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "Extract strings from binary files" in result.stdout
        assert "--encoding" in result.stdout
        assert "--filter" in result.stdout
    
    def test_cli_with_binary_file(self, tmp_path):
        """Test CLI with a binary file."""
        # Create a binary file with strings
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(
            b'\x00\x00Hello World\x00\x00test string\x00\x00'
            b'\xff\xfeP\x00y\x00t\x00h\x00o\x00n\x00\x00\x00'
        )
        
        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("test.bin", "-e", "ascii", "-e", "utf-16le")
            assert result.returncode == 0
            assert "Hello World" in result.stdout
            assert "test string" in result.stdout
            assert "Python" in result.stdout
        finally:
            os.chdir(original_cwd)
    
    def test_cli_json_output(self, tmp_path):
        """Test JSON output format."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b'\x00\x00test\x00\x00hello\x00\x00')
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("test.bin", "-t", "json")
            assert result.returncode == 0
            
            # Parse JSON output
            output_json = json.loads(result.stdout)
            assert "test.bin" in output_json
            strings = output_json["test.bin"]
            assert any("test" in s[0] for s in strings)
            assert any("hello" in s[0] for s in strings)
        finally:
            os.chdir(original_cwd)
    
    def test_cli_filter_pattern(self, tmp_path):
        """Test regex filtering."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(
            b'\x00\x00hello world\x00\x00test string\x00\x00'
            b'another hello\x00\x00goodbye\x00\x00'
        )
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("test.bin", "-f", "hello")
            assert result.returncode == 0
            assert "hello" in result.stdout
            assert "goodbye" not in result.stdout or "ggooooddbbyyee" not in result.stdout
        finally:
            os.chdir(original_cwd)
    
    def test_cli_min_max_length(self, tmp_path):
        """Test minimum and maximum length filtering."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(
            b'\x00\x00ab\x00\x00short\x00\x00'
            b'this is a medium length string\x00\x00'
            b'x' * 300 + b'\x00\x00'
        )
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("test.bin", "-m", "5", "-M", "50")
            assert result.returncode == 0
            assert "short" in result.stdout
            assert "medium length" in result.stdout
            assert "xxx" not in result.stdout  # Very long string excluded
            assert "ab" not in result.stdout  # Too short
        finally:
            os.chdir(original_cwd)
    
    def test_cli_output_to_file(self, tmp_path):
        """Test writing output to a file."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b'\x00\x00test string\x00\x00')
        output_file = tmp_path / "output.txt"
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("test.bin", "-o", str(output_file))
            assert result.returncode == 0
            assert output_file.exists()
            
            content = output_file.read_text()
            assert "test string" in content
        finally:
            os.chdir(original_cwd)
    
    def test_cli_overwrite_protection(self, tmp_path):
        """Test that existing files are protected without -y flag."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b'\x00\x00test\x00\x00')
        output_file = tmp_path / "output.txt"
        output_file.write_text("existing content")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            # Without -y flag
            result = run_cli("test.bin", "-o", str(output_file))
            assert result.returncode == 1
            assert "Output file exists" in result.stderr
            assert output_file.read_text() == "existing content"
            
            # With -y flag
            result = run_cli("test.bin", "-o", str(output_file), "-y")
            assert result.returncode == 0
            assert "test" in output_file.read_text()
        finally:
            os.chdir(original_cwd)
    
    def test_cli_multiple_files(self, tmp_path):
        """Test processing multiple files."""
        # Create multiple binary files
        (tmp_path / "file1.bin").write_bytes(b'\x00\x00file1_string\x00\x00')
        (tmp_path / "file2.bin").write_bytes(b'\x00\x00file2_string\x00\x00')
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("*.bin")
            assert result.returncode == 0
            assert "file1_string" in result.stdout
            assert "file2_string" in result.stdout
            assert "Found 2 file(s)" in result.stderr
        finally:
            os.chdir(original_cwd)
    
    def test_cli_recursive_glob(self, tmp_path):
        """Test recursive glob patterns."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "test1.bin").write_bytes(b'\x00\x00root_string\x00\x00')
        (subdir / "test2.bin").write_bytes(b'\x00\x00sub_string\x00\x00')
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("**/*.bin")
            assert result.returncode == 0
            assert "root_string" in result.stdout
            assert "sub_string" in result.stdout
        finally:
            os.chdir(original_cwd)
    
    def test_cli_no_matches(self, tmp_path):
        """Test behavior when no files match."""
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("*.nonexistent")
            assert result.returncode == 2
            assert "No files matching" in result.stderr
        finally:
            os.chdir(original_cwd)
    
    def test_cli_invalid_regex(self, tmp_path):
        """Test handling of invalid regex pattern."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b'\x00\x00test\x00\x00')
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("test.bin", "-f", "[invalid(")
            assert result.returncode == 4
            assert "Invalid filter pattern" in result.stderr
        finally:
            os.chdir(original_cwd)
    
    def test_cli_absolute_paths(self, tmp_path):
        """Test absolute path output."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b'\x00\x00test\x00\x00')
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("test.bin", "-a")
            assert result.returncode == 0
            assert str(tmp_path) in result.stdout
        finally:
            os.chdir(original_cwd)
