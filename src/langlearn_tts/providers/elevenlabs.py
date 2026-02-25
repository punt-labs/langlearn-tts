"""ElevenLabs TTS provider — re-exported from punt-tts.

Subclass overrides generate_audio/generate_audios to use
langlearn-tts output path resolution (~/langlearn-audio default).
"""

from __future__ import annotations

from collections.abc import Sequence

from langlearn_tts.output import resolve_output_path
from langlearn_tts.types import SynthesisRequest, SynthesisResult
from punt_tts.providers.elevenlabs import (
    VOICES,
    ElevenLabsProvider as _ElevenLabsProvider,
)

__all__ = ["VOICES", "ElevenLabsProvider"]


class ElevenLabsProvider(_ElevenLabsProvider):
    """ElevenLabs TTS provider with langlearn-tts output path resolution."""

    def generate_audio(self, request: SynthesisRequest) -> SynthesisResult:
        output_path = resolve_output_path(request)
        return self.synthesize(request, output_path)

    def generate_audios(
        self, requests: Sequence[SynthesisRequest]
    ) -> list[SynthesisResult]:
        return [self.generate_audio(request) for request in requests]
