"""Batch conversion utilities."""

import concurrent.futures
import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn


@dataclass
class ConversionResult:
    """Result of a single file conversion."""

    file_path: str
    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0


class BatchConverter:
    """Batch convert media files in a directory."""

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
    VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".wmv", ".flv"}
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma"}

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        output_format: str = "mp4",
        quality: str = "medium",
        parallel_workers: int = 1,
        file_filter: Optional[Callable[[Path], bool]] = None,
    ) -> None:
        """Initialize batch converter."""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_format = output_format.lower()
        self.quality = quality
        self.parallel_workers = max(1, parallel_workers)
        self.file_filter = file_filter

        self._results: list[ConversionResult] = []

    def _get_files_to_convert(self) -> list[Path]:
        """Get list of files to convert based on output format."""
        all_extensions = self.IMAGE_EXTENSIONS | self.VIDEO_EXTENSIONS | self.AUDIO_EXTENSIONS

        files = []
        for ext in all_extensions:
            files.extend(self.input_dir.glob(f"*{ext}"))
            files.extend(self.input_dir.glob(f"*{ext.upper()}"))

        if self.file_filter:
            files = [f for f in files if self.file_filter(f)]

        return sorted(set(files))

    def _get_media_type(self, file_path: Path) -> str:
        """Determine media type from file extension."""
        ext = file_path.suffix.lower()
        if ext in self.IMAGE_EXTENSIONS:
            return "image"
        elif ext in self.VIDEO_EXTENSIONS:
            return "video"
        elif ext in self.AUDIO_EXTENSIONS:
            return "audio"
        return "unknown"

    def _convert_single(self, input_file: Path) -> ConversionResult:
        """Convert a single file."""
        import time

        start_time = time.time()
        output_file = self.output_dir / f"{input_file.stem}.{self.output_format}"

        try:
            media_type = self._get_media_type(input_file)

            if media_type == "image":
                success = self._convert_image(input_file, output_file)
            elif media_type == "video":
                success = self._convert_video(input_file, output_file)
            elif media_type == "audio":
                success = self._convert_audio(input_file, output_file)
            else:
                return ConversionResult(
                    file_path=str(input_file),
                    success=False,
                    error=f"Unknown media type: {input_file.suffix}",
                )

            return ConversionResult(
                file_path=str(input_file),
                success=success,
                output_path=str(output_file) if success else None,
                error=None if success else "Conversion failed",
                duration=time.time() - start_time,
            )

        except Exception as e:
            return ConversionResult(
                file_path=str(input_file),
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )

    def _convert_image(self, input_file: Path, output_file: Path) -> bool:
        """Convert an image file."""
        try:
            from PIL import Image

            img = Image.open(input_file)

            save_kwargs: dict[str, Any] = {}
            if self.output_format in ["jpg", "jpeg"]:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                save_kwargs["quality"] = 80

            img.save(output_file, **save_kwargs)
            return True
        except Exception:
            return False

    def _convert_video(self, input_file: Path, output_file: Path) -> bool:
        """Convert a video file using ffmpeg."""
        try:
            import ffmpeg

            crf_map = {"low": 28, "medium": 23, "high": 18}
            crf = crf_map.get(self.quality, 23)

            stream = ffmpeg.input(str(input_file))
            stream = ffmpeg.output(
                stream,
                str(output_file),
                vcodec="libx264",
                acodec="aac",
                crf=crf,
                preset="medium",
            )
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            return True
        except Exception:
            return False

    def _convert_audio(self, input_file: Path, output_file: Path) -> bool:
        """Convert an audio file using pydub."""
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(str(input_file))
            audio.export(str(output_file), format=self.output_format)
            return True
        except Exception:
            return False

    def run(self) -> list[ConversionResult]:
        """Execute batch conversion."""
        files = self._get_files_to_convert()

        if not files:
            return []

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.parallel_workers > 1:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.parallel_workers
            ) as executor:
                futures = {executor.submit(self._convert_single, f): f for f in files}
                for future in concurrent.futures.as_completed(futures):
                    self._results.append(future.result())
        else:
            for file in files:
                self._results.append(self._convert_single(file))

        return self._results

    def run_with_progress(self) -> list[ConversionResult]:
        """Execute batch conversion with progress display."""
        files = self._get_files_to_convert()

        if not files:
            return []

        self.output_dir.mkdir(parents=True, exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task("Converting files...", total=len(files))

            if self.parallel_workers > 1:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=self.parallel_workers
                ) as executor:
                    futures = {executor.submit(self._convert_single, f): f for f in files}
                    for future in concurrent.futures.as_completed(futures):
                        self._results.append(future.result())
                        progress.update(task, advance=1)
            else:
                for file in files:
                    self._results.append(self._convert_single(file))
                    progress.update(task, advance=1)

        return self._results

    def get_summary(self) -> dict[str, Any]:
        """Get summary of conversion results."""
        if not self._results:
            return {"total": 0, "success": 0, "failed": 0, "total_duration": 0.0}

        success_count = sum(1 for r in self._results if r.success)
        total_duration = sum(r.duration for r in self._results)

        return {
            "total": len(self._results),
            "success": success_count,
            "failed": len(self._results) - success_count,
            "total_duration": total_duration,
            "errors": [r.error for r in self._results if r.error],
        }
