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

    Args:
        name: Provider name (e.g. 'polly', 'openai'). If None, auto-detects.
        **kwargs: Provider-specific options (e.g. model='tts-1-hd').

    Returns:
        An initialized TTSProvider instance.

    Raises:
        ValueError: If the provider name is not registered.
    """
    from punt_tts.providers import get_provider as _get_provider

    resolved = name.lower() if name is not None else auto_detect_provider()
    return _get_provider(resolved, **kwargs)
