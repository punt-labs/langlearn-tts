"""Output path helpers for TTS generation."""

from __future__ import annotations

import os
from pathlib import Path

from langlearn_tts.types import SynthesisRequest, generate_filename


def resolve_output_path(request: SynthesisRequest) -> Path:
    """Resolve output path for a synthesis request."""
    metadata = request.metadata
    output_path = metadata.get("output_path")
    if output_path:
        path = Path(output_path)
    else:
        output_dir = metadata.get("output_dir") or os.environ.get(
            "LANGLEARN_TTS_OUTPUT_DIR", "."
        )
        filename = metadata.get("filename") or generate_filename(request.text)
        path = Path(output_dir) / filename

    path.parent.mkdir(parents=True, exist_ok=True)
    return path
