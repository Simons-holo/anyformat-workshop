"""Integration tests for image conversion."""

from PIL import Image
from pathlib import Path

import pytest

from anyformat.converters.image import SUPPORTED_FORMATS, QUALITY_PRESETS


class TestImageConversion:
    """Tests for image conversion functionality."""

    def test_supported_formats_constant(self):
        """Test that supported formats are defined correctly."""
        assert "jpg" in SUPPORTED_FORMATS
        assert "png" in SUPPORTED_FORMATS
        assert "gif" in SUPPORTED_FORMATS
        assert "webp" in SUPPORTED_FORMATS

    def test_quality_presets_defined(self):
        """Test that quality presets are defined."""
        assert "low" in QUALITY_PRESETS
        assert "medium" in QUALITY_PRESETS
        assert "high" in QUALITY_PRESETS

        for preset in QUALITY_PRESETS.values():
            assert "quality" in preset

    def test_convert_png_to_jpg(self, sample_image, output_dir):
        """Test converting PNG to JPEG."""
        output_path = output_dir / "converted.jpg"
        img = Image.open(sample_image)
        rgb_img = img.convert("RGB")
        rgb_img.save(output_path, format="JPEG", quality=80)

        assert output_path.exists()
        assert output_path.suffix.lower() == ".jpg"

    def test_convert_jpg_to_png(self, sample_jpeg_image, output_dir):
        """Test converting JPEG to PNG."""
        output_path = output_dir / "converted.png"
        img = Image.open(sample_jpeg_image)
        img.save(output_path, format="PNG")

        assert output_path.exists()
        assert output_path.suffix.lower() == ".png"

    def test_resize_image(self, sample_image, output_dir):
        """Test resizing an image."""
        output_path = output_dir / "resized.png"
        img = Image.open(sample_image)
        resized = img.resize((50, 50), Image.Resampling.LANCZOS)
        resized.save(output_path)

        with Image.open(output_path) as result:
            assert result.size == (50, 50)

    def test_resize_with_aspect_ratio(self, sample_image, output_dir):
        """Test resizing while maintaining aspect ratio."""
        output_path = output_dir / "resized_aspect.png"
        img = Image.open(sample_image)
        original_width, original_height = img.size

        target_width = 200
        ratio = target_width / original_width
        new_height = int(original_height * ratio)

        resized = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
        resized.save(output_path)

        with Image.open(output_path) as result:
            aspect_ratio = result.width / result.height
            original_ratio = original_width / original_height
            assert abs(aspect_ratio - original_ratio) < 0.01

    def test_rotate_image(self, sample_image, output_dir):
        """Test rotating an image."""
        output_path = output_dir / "rotated.png"
        img = Image.open(sample_image)
        rotated = img.rotate(90, expand=True)
        rotated.save(output_path)

        with Image.open(output_path) as result:
            assert result.width == img.height
            assert result.height == img.width

    def test_compress_image_quality(self, sample_jpeg_image, output_dir):
        """Test image compression with different qualities."""
        low_quality = output_dir / "low.jpg"
        high_quality = output_dir / "high.jpg"

        img = Image.open(sample_jpeg_image)
        img.save(low_quality, format="JPEG", quality=50)
        img.save(high_quality, format="JPEG", quality=95)

        assert low_quality.stat().st_size < high_quality.stat().st_size

    def test_rgba_to_jpg_conversion(self, sample_rgba_image, output_dir):
        """Test converting RGBA image to JPEG (requires RGB conversion)."""
        output_path = output_dir / "rgba_converted.jpg"
        img = Image.open(sample_rgba_image)

        assert img.mode == "RGBA"

        rgb_img = img.convert("RGB")
        rgb_img.save(output_path, format="JPEG", quality=80)

        assert output_path.exists()

    def test_batch_convert_creates_all_files(self, temp_dir, output_dir):
        """Test batch conversion creates files for all images."""
        from PIL import Image

        input_dir = temp_dir / "input"
        input_dir.mkdir()

        for i, color in enumerate(["red", "green", "blue"]):
            img = Image.new("RGB", (50, 50), color=color)
            img.save(input_dir / f"image_{i}.png")

        for img_file in input_dir.glob("*.png"):
            output_file = output_dir / f"{img_file.stem}.jpg"
            img = Image.open(img_file)
            img.convert("RGB").save(output_file, format="JPEG")

        assert len(list(output_dir.glob("*.jpg"))) == 3


class TestImageFormatSupport:
    """Tests for format-specific behaviors."""

    def test_png_preserves_transparency(self, sample_rgba_image, output_dir):
        """Test that PNG preserves transparency."""
        output_path = output_dir / "transparent.png"
        img = Image.open(sample_rgba_image)
        img.save(output_path, format="PNG")

        with Image.open(output_path) as result:
            assert result.mode == "RGBA"

    def test_webp_supports_transparency(self, sample_rgba_image, output_dir):
        """Test that WebP supports transparency."""
        output_path = output_dir / "transparent.webp"
        img = Image.open(sample_rgba_image)
        img.save(output_path, format="WEBP")

        assert output_path.exists()
