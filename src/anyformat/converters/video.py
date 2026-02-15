"""Video conversion module using ffmpeg."""

import subprocess
from pathlib import Path
from typing import Optional

import ffmpeg
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

app = typer.Typer(help="Video conversion commands")
console = Console()

SUPPORTED_FORMATS = ["mp4", "webm", "mkv", "avi", "mov", "gif"]

QUALITY_PRESETS = {
    "low": {"crf": 28, "preset": "faster"},
    "medium": {"crf": 23, "preset": "medium"},
    "high": {"crf": 18, "preset": "slow"},
}

CODEC_MAP = {
    "mp4": {"video": "libx264", "audio": "aac"},
    "webm": {"video": "libvpx-vp9", "audio": "libopus"},
    "mkv": {"video": "libx265", "audio": "aac"},
    "avi": {"video": "mpeg4", "audio": "mp3"},
    "mov": {"video": "libx264", "audio": "aac"},
}


@app.command("convert")
def convert(
    input_path: str = typer.Argument(..., help="Path to input video file"),
    output_path: str = typer.Argument(..., help="Path to output video file"),
    quality: str = typer.Option(
        "medium", "--quality", "-q", help="Quality preset (low, medium, high)"
    ),
    codec: Optional[str] = typer.Option(None, "--codec", "-c", help="Custom video codec"),
    audio_codec: Optional[str] = typer.Option(None, "--audio-codec", help="Custom audio codec"),
    resolution: Optional[str] = typer.Option(
        None, "--resolution", "-r", help="Output resolution (e.g., 1920x1080)"
    ),
) -> None:
    """Convert a video to a different format."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    output_format = output_file.suffix.lower().lstrip(".")
    if output_format not in SUPPORTED_FORMATS:
        console.print(f"[red]Error:[/red] Unsupported output format: {output_format}")
        console.print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        raise typer.Exit(1)

    preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"])
    video_codec = codec or CODEC_MAP.get(output_format, {}).get("video", "libx264")
    audio_codec_val = audio_codec or CODEC_MAP.get(output_format, {}).get("audio", "aac")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task("Converting video...", total=None)

            stream = ffmpeg.input(str(input_file))

            if resolution:
                width, height = resolution.lower().split("x")
                stream = stream.filter("scale", width, height)

            stream = ffmpeg.output(
                stream,
                str(output_file),
                vcodec=video_codec,
                acodec=audio_codec_val,
                crf=preset["crf"],
                preset=preset["preset"],
            )

            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            progress.update(task, completed=100, total=100)

        console.print(f"[green]Success:[/green] Converted {input_path} to {output_path}")

    except ffmpeg.Error as e:
        console.print(
            f"[red]FFmpeg error:[/red] {e.stderr.decode() if e.stderr else 'Unknown error'}"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error converting video:[/red] {e}")
        raise typer.Exit(1)


@app.command("compress")
def compress(
    input_path: str = typer.Argument(..., help="Path to input video file"),
    target_size: Optional[int] = typer.Option(
        None, "--target-size", "-s", help="Target size in MB"
    ),
    quality: str = typer.Option("medium", "--quality", "-q", help="Quality preset"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Compress a video to reduce file size."""
    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_name(f"{input_file.stem}_compressed.mp4")
    else:
        output_file = Path(output_path)

    try:
        preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"])

        stream = ffmpeg.input(str(input_file))
        stream = ffmpeg.output(
            stream,
            str(output_file),
            vcodec="libx264",
            acodec="aac",
            crf=preset["crf"] + 5,
            preset="fast",
        )

        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        original_size = input_file.stat().st_size
        new_size = output_file.stat().st_size
        reduction = (1 - new_size / original_size) * 100

        console.print(f"[green]Success:[/green] Compressed video saved to {output_file}")
        console.print(f"Original size: {original_size / (1024 * 1024):.1f} MB")
        console.print(f"New size: {new_size / (1024 * 1024):.1f} MB")
        console.print(f"Reduction: {reduction:.1f}%")

    except ffmpeg.Error as e:
        console.print(
            f"[red]FFmpeg error:[/red] {e.stderr.decode() if e.stderr else 'Unknown error'}"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error compressing video:[/red] {e}")
        raise typer.Exit(1)


@app.command("extract-audio")
def extract_audio(
    input_path: str = typer.Argument(..., help="Path to input video file"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output audio file"),
    format: str = typer.Option("mp3", "--format", "-f", help="Audio format (mp3, aac, wav)"),
    bitrate: str = typer.Option("192k", "--bitrate", "-b", help="Audio bitrate"),
) -> None:
    """Extract audio from a video file."""
    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_suffix(f".{format}")
    else:
        output_file = Path(output_path)

    try:
        stream = ffmpeg.input(str(input_file))
        stream = ffmpeg.output(
            stream.audio,
            str(output_file),
            acodec="libmp3lame" if format == "mp3" else "copy",
            audio_bitrate=bitrate,
        )

        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        console.print(f"[green]Success:[/green] Audio extracted to {output_file}")

    except ffmpeg.Error as e:
        console.print(
            f"[red]FFmpeg error:[/red] {e.stderr.decode() if e.stderr else 'Unknown error'}"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error extracting audio:[/red] {e}")
        raise typer.Exit(1)


@app.command("trim")
def trim(
    input_path: str = typer.Argument(..., help="Path to input video file"),
    start: str = typer.Argument(..., help="Start time (e.g., 00:01:30 or 90)"),
    end: str = typer.Argument(..., help="End time (e.g., 00:02:00 or 120)"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Trim a video between specified timestamps."""
    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_name(f"{input_file.stem}_trimmed{input_file.suffix}")
    else:
        output_file = Path(output_path)

    try:
        start_seconds = _parse_time(start)
        end_seconds = _parse_time(end)

        if start_seconds >= end_seconds:
            console.print("[red]Error:[/red] Start time must be before end time")
            raise typer.Exit(1)

        stream = ffmpeg.input(str(input_file), ss=start_seconds, t=end_seconds - start_seconds)
        stream = ffmpeg.output(stream, str(output_file), c="copy")

        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        console.print(f"[green]Success:[/green] Trimmed video saved to {output_file}")

    except ffmpeg.Error as e:
        console.print(
            f"[red]FFmpeg error:[/red] {e.stderr.decode() if e.stderr else 'Unknown error'}"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error trimming video:[/red] {e}")
        raise typer.Exit(1)


@app.command("gif")
def to_gif(
    input_path: str = typer.Argument(..., help="Path to input video file"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output GIF file"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start time"),
    duration: Optional[int] = typer.Option(5, "--duration", "-d", help="Duration in seconds"),
    fps: int = typer.Option(10, "--fps", help="Frames per second"),
    width: int = typer.Option(480, "--width", "-w", help="Output width"),
) -> None:
    """Convert a video clip to GIF."""
    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_suffix(".gif")
    else:
        output_file = Path(output_path)

    try:
        start_time = _parse_time(start) if start else 0

        stream = ffmpeg.input(str(input_file), ss=start_time, t=duration)
        stream = stream.filter("fps", fps=fps)
        stream = stream.filter("scale", width, -1)
        stream = ffmpeg.output(stream, str(output_file))

        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        console.print(f"[green]Success:[/green] GIF saved to {output_file}")

    except ffmpeg.Error as e:
        console.print(
            f"[red]FFmpeg error:[/red] {e.stderr.decode() if e.stderr else 'Unknown error'}"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error creating GIF:[/red] {e}")
        raise typer.Exit(1)


def _parse_time(time_str: str) -> float:
    """Parse time string to seconds."""
    if ":" in time_str:
        parts = time_str.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        elif len(parts) == 2:
            minutes, seconds = parts
            return float(minutes) * 60 + float(seconds)
    return float(time_str)


@app.command("concat")
def concat_videos(
    input_files: list[str] = typer.Argument(..., help="List of video files to concatenate"),
    output_path: str = typer.Option("concatenated.mp4", "--output", "-o", help="Output file path"),
) -> None:
    """Concatenate multiple videos into one."""
    if len(input_files) < 2:
        console.print("[red]Error:[/red] At least two input files are required")
        raise typer.Exit(1)

    for input_file in input_files:
        if not Path(input_file).exists():
            console.print(f"[red]Error:[/red] File not found: {input_file}")
            raise typer.Exit(1)

    try:
        streams = [ffmpeg.input(f) for f in input_files]
        stream = ffmpeg.concat(*[s.video for s in streams] + [s.audio for s in streams], v=1, a=1)
        stream = ffmpeg.output(stream, output_path)

        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        console.print(f"[green]Success:[/green] Concatenated video saved to {output_path}")

    except ffmpeg.Error as e:
        console.print(
            f"[red]FFmpeg error:[/red] {e.stderr.decode() if e.stderr else 'Unknown error'}"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error concatenating videos:[/red] {e}")
        raise typer.Exit(1)
