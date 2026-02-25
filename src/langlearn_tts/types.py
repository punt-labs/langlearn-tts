"""Domain types for langlearn-tts.

Re-exports from punt-tts for TTS engine types, plus langlearn-types
AudioProvider protocol for the orchestrator boundary.
"""

from __future__ import annotations

from langlearn_types import AudioProvider

from punt_tts.types import (
    SUPPORTED_LANGUAGES,
    AudioProviderId,
    AudioRequest,
    AudioRequest as SynthesisRequest,
    AudioResult,
    AudioResult as SynthesisResult,
    HealthCheck,
    MergeStrategy,
    TTSProvider,
    generate_filename,
    result_to_dict,
    validate_language,
)

__all__ = [
    "SUPPORTED_LANGUAGES",
    "AudioProvider",
    "AudioProviderId",
    "AudioRequest",
    "AudioResult",
    "HealthCheck",
    "MergeStrategy",
    "SynthesisRequest",
    "SynthesisResult",
    "TTSProvider",
    "generate_filename",
    "result_to_dict",
    "validate_language",
]
