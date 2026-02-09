"""Domain types for langlearn-tts."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)

__all__ = [
    "HealthCheck",
    "MergeStrategy",
    "SynthesisRequest",
    "SynthesisResult",
    "TTSProvider",
    "generate_filename",
]


@dataclass(frozen=True)
class HealthCheck:
    """Result of a single health check."""

    passed: bool
    message: str
    required: bool = field(default=True)


class MergeStrategy(Enum):
    """Controls whether batch operations produce one file per input or one
    merged file for the entire batch."""

    ONE_FILE_PER_INPUT = "separate"
    ONE_FILE_PER_BATCH = "single"


@dataclass(frozen=True)
class SynthesisRequest:
    """A request to synthesize a single text to audio."""

    text: str
    voice: str
    rate: int = 90
    """Speech rate as a percentage (e.g. 90 = 90% speed)."""
    stability: float | None = None
    """ElevenLabs voice stability (0.0-1.0). None = provider default."""
    similarity: float | None = None
    """ElevenLabs voice similarity boost (0.0-1.0). None = provider default."""
    style: float | None = None
    """ElevenLabs voice style/expressiveness (0.0-1.0). None = provider default."""
    speaker_boost: bool | None = None
    """ElevenLabs speaker boost toggle. None = provider default."""


@dataclass(frozen=True)
class SynthesisResult:
    """The result of a synthesis operation."""

    file_path: Path
    text: str
    voice_name: str

    def to_dict(self) -> dict[str, str]:
        """Serialize to a dict suitable for MCP tool responses."""
        return {
            "file_path": str(self.file_path),
            "text": self.text,
            "voice": self.voice_name,
        }


@runtime_checkable
class TTSProvider(Protocol):
    """Provider-agnostic interface for text-to-speech engines."""

    @property
    def name(self) -> str:
        """Short identifier for this provider (e.g. 'polly')."""
        ...

    def synthesize(
        self, request: SynthesisRequest, output_path: Path
    ) -> SynthesisResult:
        """Synthesize text to an audio file.

        Args:
            request: The synthesis parameters.
            output_path: Where to write the audio file.

        Returns:
            A SynthesisResult with the file path and metadata.
        """
        ...

    def resolve_voice(self, name: str) -> str:
        """Validate and resolve a voice name.

        Args:
            name: Case-insensitive voice name.

        Returns:
            The canonical voice name.

        Raises:
            ValueError: If the voice name is not valid for this provider.
        """
        ...

    def check_health(self) -> list[HealthCheck]:
        """Run provider-specific health checks.

        Returns:
            List of HealthCheck results.
        """
        ...


def generate_filename(text: str, prefix: str = "") -> str:
    """Generate a deterministic MP3 filename from text content.

    Uses an MD5 hash of the text to produce a stable, filesystem-safe
    filename. An optional prefix is prepended for disambiguation.

    Args:
        text: The source text.
        prefix: Optional prefix (e.g. "pair_").

    Returns:
        A filename like "a1b2c3d4.mp3" or "pair_a1b2c3d4.mp3".
    """
    digest = hashlib.md5(text.encode()).hexdigest()[:12]
    if prefix:
        return f"{prefix}{digest}.mp3"
    return f"{digest}.mp3"
