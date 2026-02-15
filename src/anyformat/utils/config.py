"""Configuration management."""

import json
from pathlib import Path
from typing import Any, Optional


class Config:
    """Manage application configuration."""

    DEFAULT_CONFIG = {
        "quality": "medium",
        "output_dir": "./output",
        "parallel_workers": 1,
        "overwrite": False,
        "verbose": False,
    }

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize configuration."""
        self._config_path = Path(config_path) if config_path else self._get_default_config_path()
        self._config: dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self._load()

    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".config" / "anyformat"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    def _load(self) -> None:
        """Load configuration from file."""
        if self._config_path.exists():
            try:
                with open(self._config_path) as f:
                    loaded = json.load(f)
                    self._config.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass

    def _save(self) -> None:
        """Save configuration to file."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and persist."""
        self._config[key] = value
        self._save()

    def get_all(self) -> dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = self.DEFAULT_CONFIG.copy()
        self._save()
