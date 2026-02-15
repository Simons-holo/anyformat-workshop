"""Image conversion module."""

from pathlib import Path
from typing import Optional

import typer
from PIL import Image
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

app = typer.Typer(help="Image conversion commands")
console = Console()

SUPPORTED_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "bmp": "BMP",
    "webp": "WEBP",
    "tiff": "TIFF",
    "ico": "ICO",
}

QUALITY_PRESETS = {
    "low": {"quality": 60, "optimize": True},
    "medium": {"quality": 80, "optimize": True},
    "high": {"quality": 95, "optimize": False},
}


@app.command("convert")
def convert(
    input_path: str = typer.Argument(..., help="Path to input image file"),
    output_path: str = typer.Argument(..., help="Path to output image file"),
    quality: str = typer.Option(
        "medium", "--quality", "-q", help="Quality preset (low, medium, high)"
    ),
    resize: Optional[str] = typer.Option(
        None, "--resize", "-r", help="Resize image (e.g., 800x600)"
    ),
    compress: bool = typer.Option(False, "--compress", "-c", help="Apply compression"),
) -> None:
    """Convert an image to a different format."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    output_format = output_file.suffix.lower().lstrip(".")
    if output_format not in SUPPORTED_FORMATS:
        console.print(f"[red]Error:[/red] Unsupported output format: {output_format}")
        console.print(f"Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}")
        raise typer.Exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task("Converting image...", total=100)

            img = Image.open(input_file)
            progress.update(task, advance=20)

            if resize:
                width, height = map(int, resize.lower().split("x"))
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                progress.update(task, advance=20)

            save_kwargs = {"format": SUPPORTED_FORMATS[output_format]}
            save_kwargs.update(QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"]))

            if output_format in ["jpg", "jpeg"]:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

            if compress:
                save_kwargs["optimize"] = True

            img.save(output_file, **save_kwargs)
            progress.update(task, advance=60)

        console.print(f"[green]Success:[/green] Converted {input_path} to {output_path}")

    except Exception as e:
        console.print(f"[red]Error converting image:[/red] {e}")
        raise typer.Exit(1)


@app.command("resize")
def resize_image(
    input_path: str = typer.Argument(..., help="Path to input image file"),
    dimensions: str = typer.Argument(..., help="New dimensions (e.g., 800x600)"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    keep_aspect: bool = typer.Option(False, "--keep-aspect", "-k", help="Maintain aspect ratio"),
) -> None:
    """Resize an image to specified dimensions."""
    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    try:
        target_width, target_height = map(int, dimensions.lower().split("x"))
    except ValueError:
        console.print(
            "[red]Error:[/red] Invalid dimensions format. Use WIDTHxHEIGHT (e.g., 800x600)"
        )
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_name(f"{input_file.stem}_resized{input_file.suffix}")
    else:
        output_file = Path(output_path)

    try:
        img = Image.open(input_file)

        if keep_aspect:
            original_width, original_height = img.size
            ratio = min(target_width / original_width, target_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        img.save(output_file)
        console.print(f"[green]Success:[/green] Resized image saved to {output_file}")

    except Exception as e:
        console.print(f"[red]Error resizing image:[/red] {e}")
        raise typer.Exit(1)


@app.command("compress")
def compress_image(
    input_path: str = typer.Argument(..., help="Path to input image file"),
    quality: int = typer.Option(80, "--quality", "-q", help="Compression quality (1-100)"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Compress an image to reduce file size."""
    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if quality < 1 or quality > 100:
        console.print("[red]Error:[/red] Quality must be between 1 and 100")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_name(f"{input_file.stem}_compressed{input_file.suffix}")
    else:
        output_file = Path(output_path)

    try:
        img = Image.open(input_file)
        original_size = input_file.stat().st_size

        output_format = output_file.suffix.lower().lstrip(".")
        save_kwargs = {"format": SUPPORTED_FORMATS.get(output_format, img.format)}

        if output_format in ["jpg", "jpeg"]:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif output_format == "png":
            save_kwargs["optimize"] = True
        elif output_format == "webp":
            save_kwargs["quality"] = quality

        img.save(output_file, **save_kwargs)

        new_size = output_file.stat().st_size
        reduction = (1 - new_size / original_size) * 100

        console.print(f"[green]Success:[/green] Compressed image saved to {output_file}")
        console.print(f"Original size: {original_size:,} bytes")
        console.print(f"New size: {new_size:,} bytes")
        console.print(f"Reduction: {reduction:.1f}%")

    except Exception as e:
        console.print(f"[red]Error compressing image:[/red] {e}")
        raise typer.Exit(1)


@app.command("rotate")
def rotate_image(
    input_path: str = typer.Argument(..., help="Path to input image file"),
    angle: int = typer.Argument(..., help="Rotation angle in degrees"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    expand: bool = typer.Option(
        True, "--expand/--no-expand", help="Expand canvas to fit rotated image"
    ),
) -> None:
    """Rotate an image by specified angle."""
    input_file = Path(input_path)

    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_path}")
        raise typer.Exit(1)

    if output_path is None:
        output_file = input_file.with_name(f"{input_file.stem}_rotated{input_file.suffix}")
    else:
        output_file = Path(output_path)

    try:
        img = Image.open(input_file)
        rotated = img.rotate(angle, expand=expand, resample=Image.Resampling.BICUBIC)
        rotated.save(output_file)

        console.print(f"[green]Success:[/green] Rotated image saved to {output_file}")

    except Exception as e:
        console.print(f"[red]Error rotating image:[/red] {e}")
        raise typer.Exit(1)


@app.command("batch")
def batch_convert(
    input_dir: str = typer.Argument(..., help="Directory containing images"),
    output_dir: str = typer.Argument(..., help="Output directory"),
    format: str = typer.Option("png", "--format", "-f", help="Output format"),
    quality: str = typer.Option("medium", "--quality", "-q", help="Quality preset"),
) -> None:
    """Batch convert all images in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        console.print(f"[red]Error:[/red] Input directory not found: {input_dir}")
        raise typer.Exit(1)

    if format not in SUPPORTED_FORMATS:
        console.print(f"[red]Error:[/red] Unsupported format: {format}")
        raise typer.Exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
    images = [f for f in input_path.iterdir() if f.suffix.lower() in image_extensions]

    if not images:
        console.print("[yellow]No images found in input directory[/yellow]")
        return

    console.print(f"[cyan]Found {len(images)} images to convert[/cyan]")

    success_count = 0
    fail_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
    ) as progress:
        task = progress.add_task("Converting images...", total=len(images))

        for img_file in images:
            try:
                output_file = output_path / f"{img_file.stem}.{format}"
                img = Image.open(img_file)

                save_kwargs = {"format": SUPPORTED_FORMATS[format]}
                save_kwargs.update(QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"]))

                if format in ["jpg", "jpeg"] and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                img.save(output_file, **save_kwargs)
                success_count += 1
            except Exception as e:
                console.print(f"[red]Failed to convert {img_file.name}:[/red] {e}")
                fail_count += 1
            finally:
                progress.update(task, advance=1)

    console.print(f"\n[green]Successfully converted:[/green] {success_count} images")
    if fail_count > 0:
        console.print(f"[red]Failed:[/red] {fail_count} images")
