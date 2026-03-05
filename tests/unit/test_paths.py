"""Unit tests for path utilities."""

import platform
from pathlib import Path

import pytest

from anyformat.utils.paths import (
    change_extension,
    ensure_output_dir,
    expand_user_path,
    get_file_extension,
    is_valid_filename,
    normalize_path,
    sanitize_filename,
    validate_path,
)


class TestPathUtilities:
    """Tests for path utility functions."""

    def test_ensure_output_dir_creates_directory(self, temp_dir):
        """Test that output directory is created."""
        output_path = temp_dir / "new_output_dir"
        result = ensure_output_dir(str(output_path))

        assert output_path.exists()
        assert output_path.is_dir()
        assert result == output_path

    def test_ensure_output_dir_existing_directory(self, temp_dir):
        """Test that existing directory is returned unchanged."""
        existing = temp_dir / "existing"
        existing.mkdir()

        result = ensure_output_dir(str(existing))

        assert result == existing

    def test_ensure_output_dir_relative_path(self, temp_dir, monkeypatch):
        """Test that relative paths are resolved correctly."""
        monkeypatch.chdir(temp_dir)
        result = ensure_output_dir("output")

        # Use resolve() to handle symlinks on macOS (/var -> /private/var)
        assert result.resolve() == (temp_dir / "output").resolve()
        assert result.exists()

    def test_normalize_path_windows(self, monkeypatch):
        """Test path normalization on Windows."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        result = normalize_path("path/to/file")
        assert result == "path\\to\\file"

    def test_normalize_path_unix(self, monkeypatch):
        """Test path normalization on Unix systems."""
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        result = normalize_path("path\\to\\file")
        assert result == "path/to/file"

    def test_normalize_path_macos(self, monkeypatch):
        """Test path normalization on macOS."""
        monkeypatch.setattr(platform, "system", lambda: "Darwin")

        result = normalize_path("path\\to\\file")
        assert result == "path/to/file"

    def test_change_extension(self):
        """Test changing file extensions."""
        assert change_extension("file.txt", "md") == "file.md"
        assert change_extension("file.txt", ".md") == "file.md"
        assert change_extension("file", "txt") == "file.txt"

    def test_get_file_extension(self):
        """Test getting file extensions."""
        assert get_file_extension("file.txt") == "txt"
        assert get_file_extension("file.TXT") == "txt"
        assert get_file_extension("file.tar.gz") == "gz"

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("file<>name.txt") == "file__name.txt"
        assert sanitize_filename("  file  ") == "file"
        assert sanitize_filename("") == "unnamed"
