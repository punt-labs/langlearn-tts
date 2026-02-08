"""Domain types for langlearn-tts."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import boto3

if TYPE_CHECKING:
    from mypy_boto3_polly.literals import (
        EngineType,
        LanguageCodeType,
        VoiceIdType,
    )

logger = logging.getLogger(__name__)

# Engine preference order: best quality first.
_ENGINE_PREFERENCE: list[str] = ["neural", "generative", "long-form", "standard"]


class MergeStrategy(Enum):
    """Controls whether batch operations produce one file per input or one
    merged file for the entire batch."""

    ONE_FILE_PER_INPUT = "separate"
    ONE_FILE_PER_BATCH = "single"


@dataclass(frozen=True)
class VoiceConfig:
    """Maps a voice to its Polly parameters.

    Each VoiceConfig bundles a Polly voice ID with its required language
    code and engine type, eliminating the need for callers to know these
    implementation details.
    """

    voice_id: VoiceIdType
    language_code: LanguageCodeType
    engine: EngineType


# Cache of resolved voices, keyed by lowercase name.
# Pre-populated entries act as aliases and are never overwritten.
VOICES: dict[str, VoiceConfig] = {}

# Whether the full voice list has been fetched from the API.
_voices_loaded: bool = False


def _best_engine(supported: list[str]) -> EngineType:
    """Pick the best engine from a list of supported engines."""
    for engine in _ENGINE_PREFERENCE:
        if engine in supported:
            return engine  # type: ignore[return-value]
    return supported[0]  # type: ignore[return-value]


def _load_voices_from_api() -> None:
    """Fetch all voices from the Polly API and populate the cache."""
    global _voices_loaded
    if _voices_loaded:
        return

    client: Any = boto3.client("polly")  # pyright: ignore[reportUnknownMemberType]
    resp: dict[str, Any] = client.describe_voices()

    for voice in resp["Voices"]:
        key = voice["Id"].lower()
        if key not in VOICES:
            VOICES[key] = VoiceConfig(
                voice_id=voice["Id"],
                language_code=voice["LanguageCode"],
                engine=_best_engine(voice["SupportedEngines"]),
            )

    _voices_loaded = True
    logger.debug("Loaded %d voices from Polly API", len(VOICES))


def resolve_voice(name: str) -> VoiceConfig:
    """Resolve a voice name to its configuration.

    Checks the local cache first, then queries the Polly API to
    resolve any valid Polly voice ID.

    Args:
        name: Case-insensitive voice name (e.g. "joanna", "Lucia").

    Returns:
        The corresponding VoiceConfig.

    Raises:
        ValueError: If the voice name is not a valid Polly voice.
    """
    key = name.lower()
    if key in VOICES:
        return VOICES[key]

    _load_voices_from_api()

    if key in VOICES:
        return VOICES[key]

    available = ", ".join(sorted(VOICES))
    raise ValueError(f"Unknown voice '{name}'. Available: {available}")


@dataclass(frozen=True)
class SynthesisRequest:
    """A request to synthesize a single text to audio."""

    text: str
    voice: VoiceConfig
    rate: int = 90
    """Speech rate as a percentage (e.g. 90 = 90% speed)."""


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
