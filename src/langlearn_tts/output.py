"""Output path helpers for TTS generation."""

from __future__ import annotations

import os
from pathlib import Path

from punt_vox.types import AudioRequest as SynthesisRequest, generate_filename


def expand_path(raw: str | os.PathLike[str]) -> Path:
    """Expand shell variables and tilde in a path string."""
    return Path(os.path.expandvars(os.fspath(raw))).expanduser()


def default_output_dir() -> Path:
    """Resolve the default output directory from environment or fallback.

    Resolution order: ``TTS_OUTPUT_DIR`` env var → ``~/langlearn-audio``.
    """
    env_dir = os.environ.get("TTS_OUTPUT_DIR")
    if env_dir:
        return expand_path(env_dir)
    return Path.home() / "langlearn-audio"


def resolve_output_path(request: SynthesisRequest) -> Path:
    """Resolve output path for a synthesis request."""
    metadata = request.metadata
    output_path = metadata.get("output_path")
    if output_path:
        path = expand_path(output_path)
    else:
        output_dir_raw = metadata.get("output_dir")
        output_dir = (
            expand_path(output_dir_raw) if output_dir_raw else default_output_dir()
        )
        filename = metadata.get("filename") or generate_filename(request.text)
        path = output_dir / filename

    path.parent.mkdir(parents=True, exist_ok=True)
    return path
