"""Unit tests for batch conversion utilities."""

from pathlib import Path

import pytest

from anyformat.utils.batch import BatchConverter, ConversionResult


class TestConversionResult:
    """Tests for ConversionResult dataclass."""

    def test_successful_result(self):
        """Test creating a successful conversion result."""
        result = ConversionResult(
            file_path="/input/test.png",
            success=True,
            output_path="/output/test.jpg",
        )

        assert result.success
        assert result.error is None
        assert result.output_path == "/output/test.jpg"

    def test_failed_result(self):
        """Test creating a failed conversion result."""
        result = ConversionResult(
            file_path="/input/test.png",
            success=False,
            error="Conversion failed",
        )

        assert not result.success
        assert result.error == "Conversion failed"
        assert result.output_path is None

    def test_default_values(self):
        """Test default values for optional fields."""
        result = ConversionResult(
            file_path="/test.png",
            success=True,
        )

        assert result.output_path is None
        assert result.error is None
        assert result.duration == 0.0


class TestBatchConverter:
    """Tests for BatchConverter class."""

    def test_init_default_values(self, temp_dir):
        """Test BatchConverter initialization with defaults."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        assert converter.output_format == "mp4"
        assert converter.quality == "medium"
        assert converter.parallel_workers == 1

    def test_init_custom_values(self, temp_dir):
        """Test BatchConverter initialization with custom values."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
            output_format="webm",
            quality="high",
            parallel_workers=4,
        )

        assert converter.output_format == "webm"
        assert converter.quality == "high"
        assert converter.parallel_workers == 4

    def test_parallel_workers_minimum(self, temp_dir):
        """Test that parallel workers has a minimum of 1."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
            parallel_workers=0,
        )

        assert converter.parallel_workers == 1

        converter2 = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
            parallel_workers=-5,
        )

        assert converter2.parallel_workers == 1

    def test_get_files_to_convert_empty_dir(self, temp_dir):
        """Test getting files from empty directory."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        files = converter._get_files_to_convert()

        assert files == []

    def test_get_files_to_convert_with_images(self, temp_dir, sample_image):
        """Test getting image files from directory."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        files = converter._get_files_to_convert()

        assert len(files) == 1
        assert files[0].suffix.lower() == ".png"

    def test_get_media_type_image(self, temp_dir):
        """Test determining media type for images."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        assert converter._get_media_type(Path("test.png")) == "image"
        assert converter._get_media_type(Path("test.jpg")) == "image"
        assert converter._get_media_type(Path("test.gif")) == "image"

    def test_get_media_type_video(self, temp_dir):
        """Test determining media type for videos."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        assert converter._get_media_type(Path("test.mp4")) == "video"
        assert converter._get_media_type(Path("test.webm")) == "video"
        assert converter._get_media_type(Path("test.mkv")) == "video"

    def test_get_media_type_audio(self, temp_dir):
        """Test determining media type for audio files."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        assert converter._get_media_type(Path("test.mp3")) == "audio"
        assert converter._get_media_type(Path("test.wav")) == "audio"
        assert converter._get_media_type(Path("test.flac")) == "audio"

    def test_get_media_type_unknown(self, temp_dir):
        """Test determining media type for unknown files."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        assert converter._get_media_type(Path("test.xyz")) == "unknown"

    def test_run_empty_directory(self, temp_dir):
        """Test running converter on empty directory."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        results = converter.run()

        assert results == []

    def test_get_summary_no_results(self, temp_dir):
        """Test getting summary when no conversions have run."""
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
        )

        summary = converter.get_summary()

        assert summary["total"] == 0
        assert summary["success"] == 0

    def test_file_filter(self, temp_dir):
        """Test custom file filter function."""
        from PIL import Image

        for i in range(5):
            img = Image.new("RGB", (10, 10), color=(i * 50, 0, 0))
            img.save(temp_dir / f"image_{i}.png")

        def filter_large_files(path: Path) -> bool:
            return path.stat().st_size < 500

        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(temp_dir / "output"),
            file_filter=filter_large_files,
        )

        files = converter._get_files_to_convert()

        assert all(f.stat().st_size < 500 for f in files)


class TestBatchConverterImageConversion:
    """Tests for batch image conversion."""

    def test_convert_single_image_success(self, temp_dir, sample_image):
        """Test successful single image conversion."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(output_dir),
            output_format="jpg",
        )

        result = converter._convert_single(sample_image)

        assert result.success
        assert result.output_path is not None
        assert Path(result.output_path).suffix == ".jpg"

    def test_convert_creates_output_directory(self, temp_dir, sample_image):
        """Test that output directory is created if it doesn't exist."""
        output_dir = temp_dir / "new_output"

        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(output_dir),
            output_format="jpg",
        )

        converter.run()

        assert output_dir.exists()

    def test_run_with_multiple_images(self, temp_dir):
        """Test batch conversion with multiple images."""
        from PIL import Image

        for i in range(3):
            img = Image.new("RGB", (50, 50), color=(i * 80, 0, 0))
            img.save(temp_dir / f"test_{i}.png")

        output_dir = temp_dir / "output"
        converter = BatchConverter(
            input_dir=str(temp_dir),
            output_dir=str(output_dir),
            output_format="jpg",
        )

        results = converter.run()

        assert len(results) == 3
        assert all(r.success for r in results)
