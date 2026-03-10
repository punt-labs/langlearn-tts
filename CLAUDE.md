# CLAUDE.md

## No "Pre-existing" Excuse

There is no such thing as a "pre-existing" issue. If you see a problem — in code you wrote, code a reviewer flagged, or code you happen to be reading — you fix it. Do not classify issues as "pre-existing" to justify ignoring them. Do not suggest that something is "outside the scope of this change." If it is broken and you can see it, it is your problem now.

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

## Scratch Files

Use `.tmp/` at the project root for scratch and temporary files — never `/tmp`. The `TMPDIR` environment variable is set via `.envrc` so that `tempfile` and subprocesses automatically use it. Contents are gitignored; only `.gitkeep` is tracked.

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

langlearn-tts is a thin bridge over `punt-vox`. The TTS engine (types, core, providers) lives in punt-vox; langlearn-tts adds langlearn-specific output path resolution, branding, and the `AudioProvider` protocol from `langlearn-types`.

Module structure under `src/langlearn_tts/`:

| Module | Responsibility |
|--------|---------------|
| `types.py` | Re-exports from `punt_vox.types` (`TTSProvider`, `HealthCheck`, `SynthesisRequest`, `SynthesisResult`, `MergeStrategy`, etc.) plus `AudioProvider` protocol from `langlearn_types` for the orchestrator boundary |
| `core.py` | Re-exports `TTSClient`, `split_text`, `stitch_audio` from `punt_vox.core` |
| `output.py` | langlearn-specific output path resolution: `TTS_OUTPUT_DIR` env var → `~/langlearn-audio` default |
| `cli.py` | Click CLI — `--provider` flag, voice settings flags, synthesize, batch, pair, pair-batch, doctor, install |
| `server.py` | FastMCP server — exposes same operations as MCP tools |
| `providers/__init__.py` | Provider registry, `get_provider()`, auto-detection (ElevenLabs > Polly) |
| `providers/polly.py` | Thin subclass of `punt_vox.providers.polly.PollyProvider` — overrides `generate_audio`/`generate_audios` for langlearn output path resolution |
| `providers/openai.py` | Thin subclass of `punt_vox.providers.openai.OpenAIProvider` — same pattern |
| `providers/elevenlabs.py` | Thin subclass of `punt_vox.providers.elevenlabs.ElevenLabsProvider` — same pattern |

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

### Code Review Flow

Do **not** merge immediately after creating a PR. Expect **2–6 review cycles** before merging.

1. **Create PR** — push branch, open PR via `mcp__github__create_pull_request`. Prefer MCP GitHub tools over `gh` CLI.
2. **Request Copilot review** — use `mcp__github__request_copilot_review`.
3. **Watch for feedback in the background** — `gh pr checks <number> --watch` in a background task or separate session. Do not stop waiting. Copilot and Bugbot may take 1–3 minutes after CI completes.
4. **Read all feedback** via MCP: `mcp__github__pull_request_read` with `get_reviews` and `get_review_comments`.
5. **Take every comment seriously.** There is no such thing as "pre-existing" or "unrelated to this change" — if you can see it, you own it. If you disagree, explain why in a reply.
6. **Fix and re-push** — commit fixes, push, re-run quality gates.
7. **Repeat steps 3–6** until the latest review is **uneventful** — zero new comments, all checks green.
8. **Merge only when the last review was clean** — use `mcp__github__merge_pull_request`.

### Changelog

CHANGELOG entries are written **in the PR branch, before merge** — not retroactively on main. The entry is part of the diff that gets reviewed. If a PR changes user-facing behavior and the diff does not include a CHANGELOG entry, the PR is not ready to merge. Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format. Add entries under `[Unreleased]`. Categories: Added, Changed, Deprecated, Removed, Fixed, Security. See [Workflow standards §6](../punt-kit/standards/workflow.md) for full guidance.

### README

Update `README.md` when user-facing behavior changes — new flags, commands, defaults, providers, or config. The README is the first thing users and contributors read; if the behavior changed but the README did not, the PR is not ready to merge.

### PR/FAQ

Update `prfaq.tex` when a change shifts product direction or validates/invalidates a risk assumption. The PR/FAQ is the strategic document — feature additions, pivots, and resolved risks should be reflected there.

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

## Pre-PR Checklist

- [ ] **CHANGELOG entry included in the PR diff** under `## [Unreleased]` — if user-facing behavior changed, this is a merge blocker
- [ ] **README updated** if user-facing behavior changed (new commands, flags, providers, config)
- [ ] **PR/FAQ updated** if the change shifts product direction or validates/invalidates a risk assumption
- [ ] **Quality gates pass** — `uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run mypy src/ tests/ && uv run pyright src/ tests/ && uv run pytest tests/ -v`

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

## Available Tooling

| Tool | What It Does |
|------|-------------|
| `punt init` | Scaffold missing files (CI, config, permissions, beads) |
| `punt audit` | Check compliance against Punt Labs standards |
| `punt audit --fix` | Auto-create missing mechanical files |
| `/punt reconcile` | LLM-powered contextual reconciliation (workflows, CLAUDE.md, permissions) |
