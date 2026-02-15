"""AnyFormat CLI entry point."""

import typer
from rich.console import Console

from anyformat import __version__
from anyformat.converters import audio, image, video
from anyformat.utils.config import Config
from anyformat.utils.paths import ensure_output_dir

app = typer.Typer(
    name="anyformat",
    help="Convert media files between formats with ease",
    add_completion=True,
)

console = Console()

config = Config()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
) -> None:
    """AnyFormat - Universal media conversion CLI."""
    if version:
        console.print(f"[bold green]AnyFormat[/bold green] version {__version__}")
        raise typer.Exit()


app.add_typer(image.app, name="image", help="Convert image files")
app.add_typer(video.app, name="video", help="Convert video files")
app.add_typer(audio.app, name="audio", help="Convert audio files")


@app.command("info")
def info(
    file_path: str = typer.Argument(..., help="Path to media file"),
) -> None:
    """Display information about a media file."""
    from anyformat.utils.probe import probe_file

    try:
        info_data = probe_file(file_path)
        if info_data is None:
            console.print(f"[red]Error:[/red] Could not probe file: {file_path}")
            raise typer.Exit(1)

        console.print("\n[bold cyan]File Information[/bold cyan]")
        console.print(f"  [yellow]Path:[/yellow] {file_path}")
        console.print(f"  [yellow]Format:[/yellow] {info_data.get('format', 'unknown')}")
        console.print(f"  [yellow]Duration:[/yellow] {info_data.get('duration', 'unknown')}s")
        console.print(f"  [yellow]Size:[/yellow] {info_data.get('size', 'unknown')} bytes")

        if "video" in info_data:
            video_info = info_data["video"]
            console.print("\n[bold cyan]Video Stream[/bold cyan]")
            console.print(f"  [yellow]Codec:[/yellow] {video_info.get('codec', 'unknown')}")
            console.print(
                f"  [yellow]Resolution:[/yellow] {video_info.get('width', '?')}x{video_info.get('height', '?')}"
            )
            console.print(f"  [yellow]Frame Rate:[/yellow] {video_info.get('fps', 'unknown')}")

        if "audio" in info_data:
            audio_info = info_data["audio"]
            console.print("\n[bold cyan]Audio Stream[/bold cyan]")
            console.print(f"  [yellow]Codec:[/yellow] {audio_info.get('codec', 'unknown')}")
            console.print(
                f"  [yellow]Sample Rate:[/yellow] {audio_info.get('sample_rate', 'unknown')} Hz"
            )
            console.print(f"  [yellow]Channels:[/yellow] {audio_info.get('channels', 'unknown')}")

    except Exception as e:
        console.print(f"[red]Error probing file:[/red] {e}")
        raise typer.Exit(1)


@app.command("batch")
def batch_convert(
    input_dir: str = typer.Argument(..., help="Directory containing files to convert"),
    output_dir: str = typer.Argument(..., help="Output directory for converted files"),
    format: str = typer.Option("mp4", "--format", "-f", help="Output format"),
    quality: str = typer.Option(
        "medium", "--quality", "-q", help="Quality preset (low, medium, high)"
    ),
    parallel: int = typer.Option(1, "--parallel", "-p", help="Number of parallel conversions"),
) -> None:
    """Batch convert all media files in a directory."""
    from anyformat.utils.batch import BatchConverter

    try:
        converter = BatchConverter(
            input_dir=input_dir,
            output_dir=output_dir,
            output_format=format,
            quality=quality,
            parallel_workers=parallel,
        )
        ensure_output_dir(output_dir)
        results = converter.run()

        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        console.print(f"\n[green]Successfully converted:[/green] {success_count} files")
        if fail_count > 0:
            console.print(f"[red]Failed:[/red] {fail_count} files")
            for r in results:
                if not r.success:
                    console.print(f"  - {r.file_path}: {r.error}")

    except Exception as e:
        console.print(f"[red]Batch conversion failed:[/red] {e}")
        raise typer.Exit(1)


@app.command("config")
def configure(
    set_default_quality: str = typer.Option(
        None, "--set-quality", help="Set default quality preset"
    ),
    set_default_output: str = typer.Option(
        None, "--set-output", help="Set default output directory"
    ),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
) -> None:
    """View or update configuration settings."""
    if show:
        console.print("\n[bold cyan]Current Configuration[/bold cyan]")
        console.print(f"  [yellow]Default Quality:[/yellow] {config.get('quality', 'medium')}")
        console.print(f"  [yellow]Default Output:[/yellow] {config.get('output_dir', './output')}")
        console.print(f"  [yellow]Parallel Workers:[/yellow] {config.get('parallel_workers', 1)}")
        return

    if set_default_quality:
        valid_qualities = ["low", "medium", "high"]
        if set_default_quality not in valid_qualities:
            console.print(f"[red]Invalid quality. Must be one of: {valid_qualities}[/red]")
            raise typer.Exit(1)
        config.set("quality", set_default_quality)
        console.print(f"[green]Default quality set to:[/green] {set_default_quality}")

    if set_default_output:
        config.set("output_dir", set_default_output)
        console.print(f"[green]Default output directory set to:[/green] {set_default_output}")


if __name__ == "__main__":
    app()
