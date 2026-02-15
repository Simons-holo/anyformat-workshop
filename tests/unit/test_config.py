"""Unit tests for configuration management."""

import json
from pathlib import Path

import pytest

from anyformat.utils.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_default_config_values(self, config_path):
        """Test that default configuration values are set correctly."""
        config = Config(str(config_path))

        assert config.get("quality") == "medium"
        assert config.get("output_dir") == "./output"
        assert config.get("parallel_workers") == 1

    def test_set_and_get_value(self, config_path):
        """Test setting and getting configuration values."""
        config = Config(str(config_path))

        config.set("quality", "high")
        assert config.get("quality") == "high"

        config.set("parallel_workers", 4)
        assert config.get("parallel_workers") == 4

    def test_config_persistence(self, config_path):
        """Test that configuration persists across instances."""
        config1 = Config(str(config_path))
        config1.set("quality", "low")

        config2 = Config(str(config_path))
        assert config2.get("quality") == "low"

    def test_get_nonexistent_key(self, config_path):
        """Test getting a key that doesn't exist returns default."""
        config = Config(str(config_path))

        assert config.get("nonexistent") is None
        assert config.get("nonexistent", "default_value") == "default_value"

    def test_get_all_config(self, config_path):
        """Test getting all configuration values."""
        config = Config(str(config_path))
        all_config = config.get_all()

        assert "quality" in all_config
        assert "output_dir" in all_config
        assert "parallel_workers" in all_config

    def test_reset_config(self, config_path):
        """Test resetting configuration to defaults."""
        config = Config(str(config_path))
        config.set("quality", "high")
        config.set("parallel_workers", 8)

        config.reset()

        assert config.get("quality") == "medium"
        assert config.get("parallel_workers") == 1

    def test_handles_invalid_json(self, config_path):
        """Test that invalid JSON in config file doesn't crash."""
        with open(config_path, "w") as f:
            f.write("not valid json {{{")

        config = Config(str(config_path))
        assert config.get("quality") == "medium"

    def test_missing_config_file(self, config_path):
        """Test behavior when config file doesn't exist."""
        config = Config(str(config_path))
        assert not config_path.exists()

        config.set("quality", "high")
        assert config_path.exists()
