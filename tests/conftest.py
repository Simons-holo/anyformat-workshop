"""Pytest configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    directory = tempfile.mkdtemp()
    yield Path(directory)
    shutil.rmtree(directory, ignore_errors=True)


@pytest.fixture
def sample_image(temp_dir):
    """Create a sample image file for testing."""
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    img_path = temp_dir / "test_image.png"
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_jpeg_image(temp_dir):
    """Create a sample JPEG image for testing."""
    from PIL import Image

    img = Image.new("RGB", (200, 150), color="blue")
    img_path = temp_dir / "test_photo.jpg"
    img.save(img_path, format="JPEG", quality=85)
    return img_path


@pytest.fixture
def sample_rgba_image(temp_dir):
    """Create a sample RGBA image for testing transparency."""
    from PIL import Image

    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    img_path = temp_dir / "test_transparent.png"
    img.save(img_path)
    return img_path


@pytest.fixture
def output_dir(temp_dir):
    """Create an output directory for converted files."""
    output = temp_dir / "output"
    output.mkdir()
    return output


@pytest.fixture
def config_path(temp_dir):
    """Create a path for config file testing."""
    return temp_dir / "config.json"
