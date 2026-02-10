# Contributing to langlearn-tts

## Reporting Bugs

Open an issue at <https://github.com/jmf-pobox/langlearn-tts-mcp/issues> with:

- Steps to reproduce
- Expected vs actual behavior
- Provider (ElevenLabs, Polly, OpenAI) and Python version
- Output of `langlearn-tts doctor`

## Development Setup

```bash
git clone https://github.com/jmf-pobox/langlearn-tts-mcp.git
cd langlearn-tts-mcp
uv sync --all-extras
```

## Quality Gates

All must pass before every commit:

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/ tests/
uv run pyright src/ tests/
uv run pytest tests/ -v
```

## Testing

- Unit tests use mocks. No API keys or network access required.
- Integration tests are marked `@pytest.mark.integration` and require provider API keys.
- Mock Polly/OpenAI responses need valid MP3 bytes — create a silent segment with `AudioSegment.silent()` from pydub and export to MP3 bytes.

## Commit Messages

Format: `type(scope): description`

| Prefix | Use |
|--------|-----|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `refactor:` | Code change, no behavior change |
| `test:` | Adding or updating tests |
| `docs:` | Documentation |
| `chore:` | Build, dependencies, CI |

One logical change per commit. Quality gates pass before every commit.

## Pull Requests

1. Branch from `main` with a descriptive prefix (`feat/`, `fix/`, `docs/`, etc.)
2. Keep PRs focused — one feature or fix per PR
3. All quality gates must pass
4. Update `CHANGELOG.md` under `[Unreleased]` for user-visible changes

## Code Style

- Python 3.13+, double quotes, 88-char line limit (ruff)
- `from __future__ import annotations` in every file
- Full type annotations. mypy strict + pyright strict, zero errors.
- See `CLAUDE.md` for full coding standards

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
