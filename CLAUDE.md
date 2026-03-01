# CLAUDE.md

## Project Overview

TTS MCP server and CLI for language learning. Supports ElevenLabs (premium), AWS Polly, and OpenAI TTS.

- **Package**: `punt-langlearn-tts`
- **CLI**: `langlearn-tts`
- **MCP server**: `langlearn-tts-server`
- **Python**: 3.13+, managed with `uv`

## Build & Run

```bash
# Install with dev dependencies
uv sync --all-extras

# CLI
uv run langlearn-tts --help
uv run langlearn-tts doctor

# MCP server (stdio transport)
uv run langlearn-tts-server
```

## Quality Gates

Run after every code change. All must pass with zero violations.

```bash
uv run ruff check src/ tests/        # Lint
uv run ruff format --check src/ tests/ # Format check
uv run mypy src/ tests/               # Type check (strict)
uv run pyright src/ tests/            # Type check (strict)
uv run pytest tests/ -v               # All tests pass
```

Build validation:

```bash
uv build
uvx twine check dist/*
```

## Architecture

langlearn-tts is a thin bridge over `punt-tts`. The TTS engine (types, core, providers) lives in punt-tts; langlearn-tts adds langlearn-specific output path resolution, branding, and the `AudioProvider` protocol from `langlearn-types`.

Module structure under `src/langlearn_tts/`:

| Module | Responsibility |
|--------|---------------|
| `types.py` | Re-exports from `punt_tts.types` (`TTSProvider`, `HealthCheck`, `SynthesisRequest`, `SynthesisResult`, `MergeStrategy`, etc.) plus `AudioProvider` protocol from `langlearn_types` for the orchestrator boundary |
| `core.py` | Re-exports `TTSClient`, `split_text`, `stitch_audio` from `punt_tts.core` |
| `output.py` | langlearn-specific output path resolution: `TTS_OUTPUT_DIR` env var → `~/langlearn-audio` default |
| `cli.py` | Click CLI — `--provider` flag, voice settings flags, synthesize, batch, pair, pair-batch, doctor, install |
| `server.py` | FastMCP server — exposes same operations as MCP tools |
| `providers/__init__.py` | Provider registry, `get_provider()`, auto-detection (ElevenLabs > Polly) |
| `providers/polly.py` | Thin subclass of `punt_tts.providers.polly.PollyProvider` — overrides `generate_audio`/`generate_audios` for langlearn output path resolution |
| `providers/openai.py` | Thin subclass of `punt_tts.providers.openai.OpenAIProvider` — same pattern |
| `providers/elevenlabs.py` | Thin subclass of `punt_tts.providers.elevenlabs.ElevenLabsProvider` — same pattern |

Tests mirror source: `test_types.py`, `test_core.py`, `test_cli.py`, `test_polly_provider.py`, `test_openai_provider.py`, `test_elevenlabs_provider.py` plus `conftest.py` for shared fixtures.

## Coding Standards

Follow [Python standards](../punt-kit/standards/python.md). Project-specific additions:

- `click.ClickException` for CLI user errors (this project uses Click, not Typer).
- `logger.debug()` for synthesis details. `logger.info()` for file writes.

## Testing

Follow [Python standards — Testing](../punt-kit/standards/python.md#testing). Project-specific notes:

- Mock Polly responses need valid MP3 bytes — pydub hands files to ffmpeg which rejects fake data. Use `AudioSegment.silent(duration=50)` in fixtures.
- Use `side_effect=lambda` instead of `return_value` for fresh mocks per call.
- Integration tests requiring credentials are marked `@pytest.mark.integration`.

## Development Workflow

Follow [Workflow standards](../punt-kit/standards/workflow.md) for branch discipline, micro-commits, session close protocol, and code review flow.

### Changelog

Update `CHANGELOG.md` with every user-visible change. Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format. Add entries under `[Unreleased]`. Categories: Added, Changed, Deprecated, Removed, Fixed, Security.

### Release Workflow

Releases are automated via `release.yml`. A tag push triggers: build → TestPyPI → test-install → PyPI.

1. **Bump version** in `pyproject.toml` and `src/langlearn_tts/__init__.py` (keep in sync)
2. **Move `[Unreleased]`** entries in `CHANGELOG.md` to new version section with date
3. **Run all quality gates** — ruff, mypy, pyright, pytest
4. **Commit**: `chore: release vX.Y.Z`
5. **Build locally**: `rm -rf dist/ && uv build && uvx twine check dist/*` (validation only — do NOT upload)
6. **Tag**: `git tag vX.Y.Z`
7. **Push**: `git push origin main vX.Y.Z` (triggers GH Actions release workflow)
8. **Wait for GH Actions**: `gh run watch` — workflow builds, publishes to TestPyPI, verifies install, then publishes to PyPI
9. **GitHub release**: `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file -` (use CHANGELOG entry)
10. **Verify**: `uv tool install --upgrade punt-langlearn-tts && langlearn-tts doctor`

A release is not complete until all 10 steps are done. PyPI publishing is owned by GH Actions — never upload manually.

## Known Type Checker Workarounds

### mypy vs pyright on boto3 (in providers/polly.py)

boto3-stubs types `boto3.client("polly")` correctly for mypy but pyright sees partially unknown overloads. Solution:

```python
cast("PollyClientType", boto3.client("polly"))  # type: ignore[redundant-cast]  # pyright: ignore[reportUnknownMemberType]
```

### pydub and elevenlabs have no type stubs

Use `Any` annotations and pyright inline ignores. These are the acceptable `Any` usages. Both have `[[tool.mypy.overrides]]` with `ignore_missing_imports = true`.

## Standards

- Always find the root cause. No workarounds, no shortcuts.
- Do not suggest skipping tests, lowering standards, or ignoring failures.
- Do not present workarounds for failing tests — fix the actual problem.
- Report complete, unfiltered data.
- The user makes decisions. Ask before making up rationales.
