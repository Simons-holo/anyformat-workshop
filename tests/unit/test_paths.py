"""Unit tests for path utilities."""

import platform

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

        assert result == temp_dir / "output"
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

    def test_expand_user_path(self, monkeypatch):
        """Test user path expansion."""
        monkeypatch.setenv("HOME", "/home/testuser")

        result = expand_user_path("~/Documents")
        assert "testuser" in result

    def test_validate_path_empty(self):
        """Test that empty path is invalid."""
        is_valid, error = validate_path("")
        assert not is_valid
        assert error is not None

    def test_validate_path_valid(self, temp_dir):
        """Test validation of a valid path."""
        is_valid, error = validate_path(str(temp_dir))
        assert is_valid
        assert error is None

    def test_validate_path_must_exist(self):
        """Test validation when path must exist."""
        is_valid, error = validate_path("/nonexistent/path", must_exist=True)
        assert not is_valid
        assert "does not exist" in error

    def test_get_file_extension(self):
        """Test getting file extension."""
        assert get_file_extension("image.png") == "png"
        assert get_file_extension("video.MP4") == "mp4"
        assert get_file_extension("file") == ""
        assert get_file_extension("path/to/file.jpg") == "jpg"

    def test_change_extension(self):
        """Test changing file extension."""
        assert change_extension("image.png", "jpg") == "image.jpg"
        assert change_extension("video.mp4", ".webm") == "video.webm"
        assert change_extension("file", "txt") == "file.txt"

    def test_is_valid_filename_empty(self):
        """Test that empty filename is invalid."""
        assert not is_valid_filename("")

    def test_is_valid_filename_valid(self):
        """Test that valid filename passes."""
        assert is_valid_filename("test_file.txt")
        assert is_valid_filename("image.png")

    def test_is_valid_filename_windows_reserved(self, monkeypatch):
        """Test that Windows reserved names are invalid."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        assert not is_valid_filename("CON.txt")
        assert not is_valid_filename("PRN")
        assert not is_valid_filename("COM1.mp4")

    def test_is_valid_filename_windows_invalid_chars(self, monkeypatch):
        """Test that Windows invalid characters are caught."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        assert not is_valid_filename("file<name>.txt")
        assert not is_valid_filename("file:name.txt")
        assert not is_valid_filename("file|name.txt")

    def test_sanitize_filename_removes_invalid_chars(self, monkeypatch):
        """Test that invalid characters are replaced."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        result = sanitize_filename("file<name>.txt")
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_filename_custom_replacement(self, monkeypatch):
        """Test custom replacement character."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        result = sanitize_filename("file:name.txt", replacement="-")
        assert result == "file-name.txt"

    def test_sanitize_filename_empty_result(self):
        """Test that empty/whitespace filename gets default."""
        result = sanitize_filename("   ")
        assert result == "unnamed"
