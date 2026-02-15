"""Unit tests for probe utilities."""

from pathlib import Path

import pytest

from anyformat.utils.probe import (
    _parse_framerate,
    get_audio_info,
    get_duration,
    get_resolution,
    probe_file,
)


class TestProbeUtilities:
    """Tests for probe utility functions."""

    def test_probe_image_file(self, sample_image):
        """Test probing an image file returns correct info."""
        info = probe_file(str(sample_image))

        assert info is not None
        assert info.get("format") == "png"
        assert info.get("width") == 100
        assert info.get("height") == 100
        assert "video" in info

    def test_probe_rgba_image(self, sample_rgba_image):
        """Test probing an RGBA image."""
        info = probe_file(str(sample_rgba_image))

        assert info is not None
        assert info.get("mode") == "RGBA"

    def test_probe_nonexistent_file(self):
        """Test probing a file that doesn't exist."""
        info = probe_file("/nonexistent/file.png")

        assert info is None

    def test_probe_unknown_format(self, temp_dir):
        """Test probing a file with unknown format."""
        unknown_file = temp_dir / "file.xyz"
        unknown_file.write_text("test content")

        info = probe_file(str(unknown_file))

        assert info is not None
        assert info.get("format") == "unknown"
        assert info.get("size") > 0

    def test_parse_framerate_whole_number(self):
        """Test parsing whole number framerate."""
        assert _parse_framerate("30/1") == 30.0
        assert _parse_framerate("60/1") == 60.0

    def test_parse_framerate_fractional(self):
        """Test parsing fractional framerate."""
        result = _parse_framerate("30000/1001")
        assert abs(result - 29.97) < 0.01

    def test_parse_framerate_decimal(self):
        """Test parsing decimal framerate string."""
        assert _parse_framerate("24.0") == 24.0
        assert _parse_framerate("23.976") == 23.976

    def test_parse_framerate_invalid(self):
        """Test parsing invalid framerate returns 0."""
        assert _parse_framerate("invalid") == 0.0
        assert _parse_framerate("1/0") == 0.0

    def test_get_resolution_image(self, sample_image):
        """Test getting resolution of an image."""
        resolution = get_resolution(str(sample_image))

        assert resolution == (100, 100)

    def test_get_duration_image(self, sample_image):
        """Test getting duration of an image (should be None)."""
        duration = get_duration(str(sample_image))

        assert duration is None

    def test_get_audio_info_image(self, sample_image):
        """Test getting audio info from image returns None."""
        audio = get_audio_info(str(sample_image))

        assert audio is None

    def test_probe_file_size(self, sample_image):
        """Test that file size is included in probe info."""
        info = probe_file(str(sample_image))

        assert "size" in info
        assert info["size"] == sample_image.stat().st_size
