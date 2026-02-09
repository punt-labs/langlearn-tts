"""TTS provider registry and auto-detection."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langlearn_tts.types import TTSProvider

__all__ = ["get_provider"]

# Registry mapping provider name → factory callable.
# Factories are lazy (no imports at module level) to avoid loading
# boto3/httpx/etc when the provider isn't used.
PROVIDER_REGISTRY: dict[str, Callable[[], TTSProvider]] = {}


def _register_polly() -> TTSProvider:
    from langlearn_tts.providers.polly import PollyProvider

    return PollyProvider()


PROVIDER_REGISTRY["polly"] = _register_polly


def auto_detect_provider() -> str:
    """Detect the best available provider from environment.

    Checks LANGLEARN_TTS_PROVIDER env var first.
    Defaults to 'polly'.
    """
    env = os.environ.get("LANGLEARN_TTS_PROVIDER")
    if env:
        return env.lower()
    return "polly"


def get_provider(name: str | None = None) -> TTSProvider:
    """Look up a provider by name, or auto-detect.

    Args:
        name: Provider name (e.g. 'polly'). If None, auto-detects.

    Returns:
        An initialized TTSProvider instance.

    Raises:
        ValueError: If the provider name is not registered.
    """
    resolved = name if name is not None else auto_detect_provider()
    factory = PROVIDER_REGISTRY.get(resolved)
    if factory is None:
        available = ", ".join(sorted(PROVIDER_REGISTRY))
        msg = f"Unknown provider '{resolved}'. Available: {available}"
        raise ValueError(msg)
    return factory()
