"""Media file probing utilities."""

import json
import subprocess
from pathlib import Path
from typing import Any, Optional


def probe_file(file_path: str) -> Optional[dict[str, Any]]:
    """Probe a media file and return information about it.

    Uses ffprobe to extract metadata from audio/video files.
    For images, uses basic file info.
    """
    path = Path(file_path)

    if not path.exists():
        return None

    extension = path.suffix.lower()

    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".ico"}
    if extension in image_extensions:
        return _probe_image(path)

    media_extensions = {
        ".mp3",
        ".wav",
        ".ogg",
        ".flac",
        ".aac",
        ".m4a",
        ".wma",
        ".mp4",
        ".webm",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
    }
    if extension in media_extensions:
        return _probe_media(path)

    return {"format": "unknown", "size": path.stat().st_size}


def _probe_image(path: Path) -> dict[str, Any]:
    """Probe an image file using PIL."""
    try:
        from PIL import Image

        with Image.open(path) as img:
            return {
                "format": img.format.lower() if img.format else "unknown",
                "size": path.stat().st_size,
                "width": img.width,
                "height": img.height,
                "mode": img.mode,
                "video": {
                    "codec": img.format.lower() if img.format else "unknown",
                    "width": img.width,
                    "height": img.height,
                },
            }
    except ImportError:
        return {
            "format": path.suffix.lower().lstrip("."),
            "size": path.stat().st_size,
        }
    except Exception:
        return {
            "format": path.suffix.lower().lstrip("."),
            "size": path.stat().st_size,
        }


def _probe_media(path: Path) -> Optional[dict[str, Any]]:
    """Probe a media file using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        data = json.loads(result.stdout)
        info: dict[str, Any] = {
            "format": data.get("format", {}).get("format_name", "unknown"),
            "duration": float(data.get("format", {}).get("duration", 0)),
            "size": int(data.get("format", {}).get("size", 0)),
        }

        for stream in data.get("streams", []):
            codec_type = stream.get("codec_type")
            if codec_type == "video":
                info["video"] = {
                    "codec": stream.get("codec_name", "unknown"),
                    "width": stream.get("width"),
                    "height": stream.get("height"),
                    "fps": _parse_framerate(stream.get("r_frame_rate", "0/1")),
                    "bit_rate": stream.get("bit_rate"),
                }
            elif codec_type == "audio":
                info["audio"] = {
                    "codec": stream.get("codec_name", "unknown"),
                    "sample_rate": stream.get("sample_rate"),
                    "channels": stream.get("channels"),
                    "bit_rate": stream.get("bit_rate"),
                }

        return info

    except subprocess.CalledProcessError:
        return None
    except json.JSONDecodeError:
        return None
    except FileNotFoundError:
        return {
            "format": path.suffix.lower().lstrip("."),
            "size": path.stat().st_size,
            "error": "ffprobe not found",
        }


def _parse_framerate(framerate_str: str) -> float:
    """Parse framerate string like '30/1' or '30000/1001'."""
    try:
        if "/" in framerate_str:
            num, den = framerate_str.split("/")
            return float(num) / float(den)
        return float(framerate_str)
    except (ValueError, ZeroDivisionError):
        return 0.0


def get_duration(file_path: str) -> Optional[float]:
    """Get the duration of a media file in seconds."""
    info = probe_file(file_path)
    if info:
        return info.get("duration")
    return None


def get_resolution(file_path: str) -> Optional[tuple[int, int]]:
    """Get the resolution of a video or image file."""
    info = probe_file(file_path)
    if info and "video" in info:
        video = info["video"]
        return (video.get("width"), video.get("height"))
    return None


def get_audio_info(file_path: str) -> Optional[dict[str, Any]]:
    """Get audio stream information from a media file."""
    info = probe_file(file_path)
    if info:
        return info.get("audio")
    return None
