"""Audio conversion module using pydub."""

import os
import subprocess
from pathlib import Path
from typing import Optional

import typer
from pydub import AudioSegment
from pydub.effects import normalize
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

app = typer.Typer(help="Audio conversion commands")
console = Console()

SUPPORTED_FORMATS = ["mp3", "wav", "ogg", "flac", "aac", "m4a", "wma"]

QUALITY_PRESETS = {
    "low": {"bitrate": "128k"},
    "medium": {"bitrate": "192k"},
    "high": {"bitrate": "320k"},
}


def _check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@app.command("convert")
def convert(
    input_path: str = typer.Argument(..., help="Path to input audio file"),
    output_path: str = typer.Argument(..., help="Path to output audio file"),
    quality: str = typer.Option(
        "medium", "--quality", "-q", help="Quality preset (low, medium, high)"
    ),
    bitrate: Optional[str] = typer.Option(
        None, "--bitrate", "-b", help="Custom bitrate (e.g., 256k)"
    ),
) -> None:
    """Convert an audio file to a different format."""
    if not _check_ffmpeg():
        console.print("[red]Error:[/red] ffmpeg is required but not installed or not in PATH")
        raise typer.Exit(1)

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
    final_bitrate = bitrate or preset["bitrate"]

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task("Converting audio...", total=100)

            audio = AudioSegment.from_file(str(input_file))
            progress.update(task, advance=30)

            export_kwargs = {"format": output_format}
            if output_format in ["mp3", "aac", "m4a"]:
                export_kwargs["bitrate"] = final_bitrate

            audio.export(str(output_file), **export_kwargs)
            progress.update(task, advance=70)

        console.print(f"[green]Success:[/green] Converted {input_path} to {output_path}")

    except Exception as e:
        console.print(f"[red]Error converting audio:[/red] {e}")
        raise typer.Exit(1)


@app.command("trim")
def trim(
    input_path: str = typer.Argument(..., help="Path to input audio file"),
    start: float = typer.Argument(..., help="Start time in seconds"),
    end: float = typer.Argument(..., help="End time in seconds"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Trim an audio file between specified times."""
    if not _check_ffmpeg():
        console.print("[red]Error:[/red] ffmpeg is required but not installed or not in PATH")
        raise typer.Exit(1)

    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if start >= end:
        console.print("[red]Error:[/red] Start time must be before end time")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_name(f"{input_file.stem}_trimmed{input_file.suffix}")
    else:
        output_file = Path(output_path)

    try:
        audio = AudioSegment.from_file(str(input_file))

        start_ms = int(start * 1000)
        end_ms = int(end * 1000)

        trimmed = audio[start_ms:end_ms]

        output_format = output_file.suffix.lower().lstrip(".")
        trimmed.export(str(output_file), format=output_format)

        console.print(f"[green]Success:[/green] Trimmed audio saved to {output_file}")

    except Exception as e:
        console.print(f"[red]Error trimming audio:[/red] {e}")
        raise typer.Exit(1)


@app.command("merge")
def merge(
    input_files: list[str] = typer.Argument(..., help="Audio files to merge"),
    output_path: str = typer.Option("merged.mp3", "--output", "-o", help="Output file path"),
    crossfade: int = typer.Option(
        0, "--crossfade", "-c", help="Crossfade duration in milliseconds"
    ),
) -> None:
    """Merge multiple audio files into one."""
    if not _check_ffmpeg():
        console.print("[red]Error:[/red] ffmpeg is required but not installed or not in PATH")
        raise typer.Exit(1)

    if len(input_files) < 2:
        console.print("[red]Error:[/red] At least two input files are required")
        raise typer.Exit(1)

    for input_file in input_files:
        if not Path(input_file).exists():
            console.print(f"[red]Error:[/red] File not found: {input_file}")
            raise typer.Exit(1)

    try:
        segments = [AudioSegment.from_file(f) for f in input_files]

        if crossfade > 0:
            merged = segments[0]
            for segment in segments[1:]:
                merged = merged.append(segment, crossfade=crossfade)
        else:
            merged = sum(segments)

        output_format = Path(output_path).suffix.lower().lstrip(".")
        merged.export(output_path, format=output_format)

        console.print(f"[green]Success:[/green] Merged audio saved to {output_path}")

    except Exception as e:
        console.print(f"[red]Error merging audio:[/red] {e}")
        raise typer.Exit(1)


@app.command("normalize")
def normalize_audio(
    input_path: str = typer.Argument(..., help="Path to input audio file"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    target_db: float = typer.Option(-20.0, "--target", "-t", help="Target dB level"),
) -> None:
    """Normalize audio volume levels."""
    if not _check_ffmpeg():
        console.print("[red]Error:[/red] ffmpeg is required but not installed or not in PATH")
        raise typer.Exit(1)

    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_name(f"{input_file.stem}_normalized{input_file.suffix}")
    else:
        output_file = Path(output_path)

    try:
        audio = AudioSegment.from_file(str(input_file))
        normalized = normalize(audio, headroom=target_db)

        output_format = output_file.suffix.lower().lstrip(".")
        normalized.export(str(output_file), format=output_format)

        console.print(f"[green]Success:[/green] Normalized audio saved to {output_file}")
        console.print(f"Target level: {target_db} dB")

    except Exception as e:
        console.print(f"[red]Error normalizing audio:[/red] {e}")
        raise typer.Exit(1)


@app.command("split")
def split(
    input_path: str = typer.Argument(..., help="Path to input audio file"),
    chunk_duration: int = typer.Argument(..., help="Chunk duration in seconds"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
) -> None:
    """Split an audio file into chunks of specified duration."""
    if not _check_ffmpeg():
        console.print("[red]Error:[/red] ffmpeg is required but not installed or not in PATH")
        raise typer.Exit(1)

    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if output_dir is None:
        output_path = input_file.parent / f"{input_file.stem}_chunks"
    else:
        output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    try:
        audio = AudioSegment.from_file(str(input_file))
        chunk_ms = chunk_duration * 1000
        total_chunks = len(audio) // chunk_ms + (1 if len(audio) % chunk_ms else 0)

        input_format = input_file.suffix.lower().lstrip(".")

        for i in range(total_chunks):
            start = i * chunk_ms
            end = min((i + 1) * chunk_ms, len(audio))
            chunk = audio[start:end]
            chunk_file = output_path / f"{input_file.stem}_part{i + 1:03d}.{input_format}"
            chunk.export(str(chunk_file), format=input_format)

        console.print(f"[green]Success:[/green] Split into {total_chunks} chunks")
        console.print(f"Output directory: {output_path}")

    except Exception as e:
        console.print(f"[red]Error splitting audio:[/red] {e}")
        raise typer.Exit(1)


@app.command("volume")
def adjust_volume(
    input_path: str = typer.Argument(..., help="Path to input audio file"),
    change_db: float = typer.Argument(..., help="Volume change in dB (negative to reduce)"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Adjust audio volume by specified dB amount."""
    if not _check_ffmpeg():
        console.print("[red]Error:[/red] ffmpeg is required but not installed or not in PATH")
        raise typer.Exit(1)

    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_name(f"{input_file.stem}_volume{input_file.suffix}")
    else:
        output_file = Path(output_path)

    try:
        audio = AudioSegment.from_file(str(input_file))
        adjusted = audio + change_db

        output_format = output_file.suffix.lower().lstrip(".")
        adjusted.export(str(output_file), format=output_format)

        console.print(f"[green]Success:[/green] Volume adjusted audio saved to {output_file}")
        console.print(f"Volume change: {change_db:+.1f} dB")

    except Exception as e:
        console.print(f"[red]Error adjusting volume:[/red] {e}")
        raise typer.Exit(1)


@app.command("info")
def audio_info(
    input_path: str = typer.Argument(..., help="Path to audio file"),
) -> None:
    """Display information about an audio file."""
    if not _check_ffmpeg():
        console.print("[red]Error:[/red] ffmpeg is required but not installed or not in PATH")
        raise typer.Exit(1)

    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] File not found: {input_path}")
        raise typer.Exit(1)

    try:
        audio = AudioSegment.from_file(str(input_file))

        console.print("\n[bold cyan]Audio Information[/bold cyan]")
        console.print(f"  [yellow]File:[/yellow] {input_path}")
        console.print(f"  [yellow]Duration:[/yellow] {len(audio) / 1000:.2f} seconds")
        console.print(f"  [yellow]Channels:[/yellow] {audio.channels}")
        console.print(f"  [yellow]Sample Rate:[/yellow] {audio.frame_rate} Hz")
        console.print(f"  [yellow]Sample Width:[/yellow] {audio.sample_width * 8} bits")
        console.print(f"  [yellow]File Size:[/yellow] {input_file.stat().st_size:,} bytes")

    except Exception as e:
        console.print(f"[red]Error reading audio file:[/red] {e}")
        raise typer.Exit(1)
