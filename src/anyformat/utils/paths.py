"""Path utilities for cross-platform compatibility."""

import os
import platform
import re
from pathlib import Path
from typing import Optional


def ensure_output_dir(output_path: str) -> Path:
    """Ensure output directory exists and return Path object.

    Handles cross-platform path differences:
    - Windows: C:\\Users\\... or \\\\server\\share\\...
    - Unix: /home/user/...
    - Relative paths on all platforms
    """
    path = Path(output_path)

    if not path.is_absolute():
        path = Path.cwd() / path

    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_path(path: str) -> str:
    """Normalize a path string for the current platform.

    Converts forward slashes to backslashes on Windows,
    and ensures consistent path separators.
    """
    if platform.system() == "Windows":
        return path.replace("/", "\\")
    return path.replace("\\", "/")


def expand_user_path(path: str) -> str:
    """Expand user home directory (~) in path."""
    return os.path.expanduser(path)


def validate_path(path: str, must_exist: bool = False) -> tuple[bool, Optional[str]]:
    """Validate a file or directory path.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Path cannot be empty"

    try:
        expanded = expand_user_path(path)
        normalized = normalize_path(expanded)
        p = Path(normalized)

        if must_exist and not p.exists():
            return False, f"Path does not exist: {path}"

        if platform.system() == "Windows":
            invalid_chars = '<>:"|?*'
            for char in invalid_chars:
                if char in str(p):
                    return False, f"Invalid character in path: {char}"
        else:
            if "\x00" in str(p):
                return False, "Path contains null byte"

        return True, None

    except Exception as e:
        return False, f"Invalid path: {e}"


def get_file_extension(path: str) -> str:
    """Get file extension without the leading dot."""
    return Path(path).suffix.lower().lstrip(".")


def change_extension(path: str, new_extension: str) -> str:
    """Change file extension to new_extension."""
    p = Path(path)
    new_ext = new_extension if new_extension.startswith(".") else f".{new_extension}"
    return str(p.with_suffix(new_ext))


def is_valid_filename(filename: str) -> bool:
    """Check if a filename is valid for the current platform."""
    if not filename:
        return False

    if platform.system() == "Windows":
        invalid_chars = '<>:"/\\|?*'
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        name = Path(filename).stem.upper()
        if any(c in filename for c in invalid_chars):
            return False
        if name in reserved_names:
            return False
        if filename.endswith(".") or filename.endswith(" "):
            return False

    return True


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Sanitize a filename by replacing invalid characters."""
    if platform.system() == "Windows":
        invalid_chars = r'[<>:"/\\|?*]'
    else:
        invalid_chars = r"[/\x00]"

    sanitized = re.sub(invalid_chars, replacement, filename)

    sanitized = sanitized.strip(". ")
    if not sanitized:
        sanitized = "unnamed"

    return sanitized
