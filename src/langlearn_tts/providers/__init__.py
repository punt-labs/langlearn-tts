"""TTS provider registry and auto-detection."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from punt_tts.providers import DEFAULT_VOICES, format_voice_hint

if TYPE_CHECKING:
    from langlearn_tts.types import TTSProvider

__all__ = [
    "DEFAULT_VOICES",
    "auto_detect_provider",
    "format_voice_hint",
    "get_provider",
]


def auto_detect_provider() -> str:
    """Detect the provider from environment.

    Checks TTS_PROVIDER env var first.
    Falls back to elevenlabs if ELEVENLABS_API_KEY is set.
    Otherwise defaults to polly.
    """
    env = os.environ.get("TTS_PROVIDER")
    if env:
        return env.lower()
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs"
    return "polly"


def get_provider(name: str | None = None, **kwargs: str | None) -> TTSProvider:
    """Look up a provider by name, or auto-detect.

    Returns langlearn-tts subclasses (not punt-tts base classes) so that
    ``generate_audio``/``generate_audios`` use langlearn-specific output
    path resolution (``~/langlearn-audio``).

    Args:
        name: Provider name (e.g. 'polly', 'openai'). If None, auto-detects.
        **kwargs: Provider-specific options (e.g. model='tts-1-hd').

    Returns:
        An initialized TTSProvider instance.

    Raises:
        ValueError: If the provider name is not registered.
    """
    from langlearn_tts.providers.elevenlabs import ElevenLabsProvider
    from langlearn_tts.providers.openai import OpenAIProvider
    from langlearn_tts.providers.polly import PollyProvider

    resolved = name.lower() if name is not None else auto_detect_provider()
    if resolved == "polly":
        return PollyProvider(**kwargs)  # type: ignore[arg-type]
    if resolved == "openai":
        return OpenAIProvider(**kwargs)  # type: ignore[arg-type]
    if resolved == "elevenlabs":
        return ElevenLabsProvider(**kwargs)
    msg = f"Unknown provider {resolved!r}. Choose from: polly, openai, elevenlabs."
    raise ValueError(msg)
