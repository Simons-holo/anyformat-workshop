# AnyFormat CLI Workshop

A hands-on learning repository for practicing open source contributions. This is a **real, functional CLI tool** for converting media files between formats, with intentionally seeded issues for contributors to fix.

> **Note:** This repository contains intentional bugs and incomplete features designed for educational purposes. It is fully functional but needs improvements to become production-ready.

## Features

- **Image Conversion**: Convert between PNG, JPEG, GIF, WebP, BMP, TIFF formats
- **Video Conversion**: Convert videos using ffmpeg (MP4, WebM, MKV, AVI, MOV)
- **Audio Conversion**: Convert audio files using pydub (MP3, WAV, FLAC, OGG, AAC)
- **Batch Processing**: Convert multiple files at once with parallel support
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Beautiful Output**: Rich terminal UI with progress bars and colors

## Learning Objectives

By contributing to this project, you will learn:

1. **Git & GitHub workflows** - Forking, branching, commits, pull requests
2. **Python packaging** - Modern pyproject.toml with uv package manager
3. **CLI development** - Typer framework with Rich for terminal output
4. **Media processing** - Image (Pillow), Video (ffmpeg), Audio (pydub)
5. **Testing** - pytest with fixtures and coverage
6. **Code quality** - Linting, type hints, documentation

## Quick Start

### Standard Setup

```bash
# Clone the repository
git clone https://github.com/anxkhn/anyformat-workshop.git
cd anyformat-workshop

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Verify installation
uv run anyformat --version

# Run tests
uv run pytest

# Run linting
uv run ruff check src/
```

### Using github.dev

1. Open the repository on GitHub
2. Press `.` (period) to open in github.dev
3. Make changes in the browser-based editor
4. Commit and create PR directly from the editor

## Project Structure

```
anyformat-workshop/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/
│   │   ├── commit-check.yml
│   │   └── pr-description-check.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── src/
│   └── anyformat/
│       ├── __init__.py
│       ├── cli.py              # Main CLI entry point
│       ├── converters/
│       │   ├── __init__.py
│       │   ├── audio.py        # Audio conversion commands
│       │   ├── image.py        # Image conversion commands
│       │   └── video.py        # Video conversion commands
│       └── utils/
│           ├── __init__.py
│           ├── batch.py        # Batch conversion logic
│           ├── config.py       # Configuration management
│           ├── paths.py        # Cross-platform path utilities
│           └── probe.py        # Media file probing
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── integration/
│   │   └── test_image_conversion.py
│   └── unit/
│       ├── test_batch.py
│       ├── test_config.py
│       ├── test_paths.py
│       └── test_probe.py
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
└── README.md
```

## Test Commands

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/
```

## Issue Labels Guide

| Label | Color | Description |
|-------|-------|-------------|
| `good-first-issue` | Blue | Easy issues for newcomers (15-30 min) |
| `intermediate` | Yellow | Moderate difficulty (1-2 hours) |
| `advanced` | Orange | Complex challenges (3-6 hours) |
| `bug` | Red | Something isn't working |
| `documentation` | Dark Blue | Improvements to docs |
| `tests` | Cyan | Related to testing |
| `enhancement` | Light Cyan | New feature or request |
| `security` | Red | Security vulnerability |
| `performance` | Yellow | Performance optimization |
| `refactoring` | Yellow | Code quality improvements |
| `ci-cd` | Gray | CI/CD pipeline issues |

## Commands Reference

### Image Commands

```bash
# Convert image format
anyformat image convert input.png output.jpg --quality high

# Resize image
anyformat image resize input.png 800x600 --keep-aspect

# Compress image
anyformat image compress input.jpg --quality 80

# Rotate image
anyformat image rotate input.png 90

# Batch convert
anyformat image batch ./images ./output --format webp
```

### Video Commands

```bash
# Convert video
anyformat video convert input.mp4 output.webm --quality medium

# Compress video
anyformat video compress input.mp4 --output compressed.mp4

# Extract audio
anyformat video extract-audio video.mp4 --format mp3

# Trim video
anyformat video trim video.mp4 00:01:00 00:02:00

# Create GIF
anyformat video gif video.mp4 --duration 5 --fps 15
```

### Audio Commands

```bash
# Convert audio
anyformat audio convert input.wav output.mp3 --quality high

# Trim audio
anyformat audio trim audio.mp3 10.0 30.0

# Merge audio files
anyformat audio merge track1.mp3 track2.mp3 --output merged.mp3

# Normalize audio
anyformat audio normalize audio.mp3 --target -20.0

# Split audio
anyformat audio split podcast.mp3 60 --output ./chunks
```

### General Commands

```bash
# Show file info
anyformat info media.mp4

# Batch convert directory
anyformat batch ./input ./output --format mp4 --parallel 4

# Configure settings
anyformat config --set-quality high --set-output ./converted
anyformat config --show
```

## Dependencies

- **Python**: >=3.13
- **ffmpeg**: Required for video and audio processing

Install ffmpeg:
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Setting up your development environment
- Creating branches and commits
- Opening pull requests
- Code style guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This repository is designed as an educational resource for learning open source contribution workflows. The seeded issues represent realistic bugs and improvements that could occur in any real project.
---

## Troubleshooting

### Common Issues and Solutions

#### 1. ffmpeg not found error

**Problem**: `FileNotFoundError: ffmpeg not found`

**Solution**: Install ffmpeg:
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Windows: Download from https://ffmpeg.org/download.html

#### 2. Permission denied errors

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
- Check file permissions: `ls -la`
- Fix permissions: `chmod +x your_script.py`
- Or run with appropriate user permissions

#### 3. Invalid format errors

**Problem**: `ValueError: Invalid format specified`

**Solution**:
- Ensure format is one of: json, csv, xlsx, parquet
- Check the file extension matches the format
- Verify the file is not corrupted

#### 4. Python version errors

**Problem**: `SyntaxError` or import errors

**Solution**:
- Ensure Python 3.10+ is installed
- Check version: `python --version`
- Create fresh virtual environment: `python -m venv venv && source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

#### 5. Module not found

**Problem**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
- Install missing package: `pip install xxx`
- Or install all requirements: `pip install -r requirements.txt`

#### 6. Path issues on Windows

**Problem**: Paths not working correctly

**Solution**:
- Use raw strings for paths: `r"C:\path\to\file"`
- Use pathlib: `from pathlib import Path`
- Forward slashes work in Python: `"C:/path/to/file"`

#### 7. Encoding errors

**Problem**: `UnicodeDecodeError` when reading files

**Solution**:
- Specify encoding: `open(file, encoding='utf-8')`
- Handle errors: `open(file, encoding='utf-8', errors='ignore')`

---

For more help, please open an issue on GitHub.
