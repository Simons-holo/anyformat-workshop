# Contributing to AnyFormat

Thank you for your interest in contributing! This guide will help you make your first contribution.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Commit Guidelines](#commit-guidelines)
4. [Code Style](#code-style)
5. [Testing Requirements](#testing-requirements)
6. [Pull Request Process](#pull-request-process)
7. [Common Mistakes](#common-mistakes)
8. [Getting Help](#getting-help)

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/anyformat-workshop.git
cd anyformat-workshop

# Add upstream remote
git remote add upstream https://github.com/anxkhn/anyformat-workshop.git
```

### 2. Set Up Environment

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Verify installation
uv run anyformat --version
```

### 3. Create a Branch

```bash
# Update main branch
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b fix/issue-number-brief-description
# or
git checkout -b feat/brief-description
# or
git checkout -b docs/brief-description
```

## Development Workflow

1. **Pick an issue** from the [Issues page](https://github.com/anxkhn/anyformat-workshop/issues)
2. **Comment** on the issue to claim it
3. **Create a branch** following the naming convention
4. **Make changes** following code style guidelines
5. **Write/update tests** for your changes
6. **Run tests** to ensure they pass
7. **Commit** with a descriptive message
8. **Push** to your fork
9. **Open a Pull Request**

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding or fixing tests |
| `chore` | Maintenance tasks |

### Examples

```bash
# Good commit messages
git commit -m "fix(image): correct RGBA to RGB conversion for JPEG"
git commit -m "docs: update installation instructions for Windows"
git commit -m "test(batch): add tests for parallel conversion"
git commit -m "feat(video): add support for custom codec selection"

# Bad commit messages (will fail CI)
git commit -m "fixed bug"
git commit -m "updated code"
git commit -m "changes"
```

### Scopes

Use appropriate scope for your changes:
- `image` - Image conversion module
- `video` - Video conversion module  
- `audio` - Audio conversion module
- `config` - Configuration
- `paths` - Path utilities
- `batch` - Batch processing
- `probe` - Media probing
- `cli` - Command line interface

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) conventions
- Maximum line length: 100 characters
- Use type hints for function signatures
- Write docstrings for public functions and classes

### Example

```python
def convert_image(
    input_path: str,
    output_path: str,
    quality: str = "medium",
) -> None:
    """Convert an image to a different format.

    Args:
        input_path: Path to the input image file.
        output_path: Path to the output image file.
        quality: Quality preset (low, medium, high).

    Raises:
        FileNotFoundError: If input file doesn't exist.
        ValueError: If output format is not supported.
    """
    pass
```

### Running Linter

```bash
# Check for issues
uv run ruff check src/

# Auto-fix issues
uv run ruff check --fix src/

# Format code
uv run ruff format src/
```

## Testing Requirements

### Test Coverage

- All new features must have tests
- Bug fixes should include regression tests
- Maintain minimum 70% coverage for new code

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run only failing tests (useful for debugging)
uv run pytest -x
```

### Test Structure

```python
class TestFeatureName:
    """Tests for feature X."""

    def test_normal_case(self, temp_dir):
        """Test normal operation."""
        pass

    def test_edge_case(self, temp_dir):
        """Test edge cases and boundary conditions."""
        pass

    def test_error_handling(self, temp_dir):
        """Test error conditions and exceptions."""
        pass
```

## Pull Request Process

### Before Submitting

1. All tests pass locally
2. Code passes linter
3. Branch is up to date with upstream/main
4. Commit messages follow conventions
5. PR description is complete

### PR Template

Your PR should include:

- Reference to the issue being fixed
- Description of changes made
- How to test the changes
- Any breaking changes or migration notes

### Review Process

1. Automated checks must pass (commit format, PR description)
2. At least one maintainer review required
3. Address all review comments
4. Squash commits if requested

### After Merge

- Delete your feature branch
- Update your local main branch
- Celebrate your contribution!

## Common Mistakes to Avoid

### Git Mistakes

1. **Committing to main** - Always create a feature branch
2. **Large commits** - Break changes into logical, atomic commits
3. **Missing upstream updates** - Regularly fetch and merge upstream
4. **Ignoring CI failures** - Fix issues before requesting review

### Code Mistakes

1. **Hardcoded paths** - Use cross-platform path utilities
2. **Missing error handling** - Handle exceptions gracefully
3. **Ignoring type hints** - Maintain type safety
4. **No documentation** - Document public APIs

### Testing Mistakes

1. **Testing only happy path** - Include edge cases and errors
2. **Using global state** - Use fixtures for isolation
3. **Ignoring test failures** - Fix failing tests before PR
4. **Missing assertions** - Every test needs assertions

## Getting Help

### Resources

- [GitHub Docs](https://docs.github.com/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

### Questions

1. Check existing issues for similar problems
2. Read the issue description carefully for hints
3. Ask questions in the issue comments
4. Use the `help wanted` label for guidance

### Stuck?

If you're stuck on an issue:

1. Re-read the acceptance criteria
2. Check the "Files to Investigate" section
3. Look at the suggested approach
4. Review similar code in the project
5. Ask for help in the issue comments

---

We appreciate every contribution, no matter how small. Thank you for helping improve AnyFormat!