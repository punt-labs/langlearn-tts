"""TTS provider registry and auto-detection."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langlearn_tts.types import TTSProvider

__all__ = ["auto_detect_provider", "get_provider"]

# Registry mapping provider name → factory callable.
# Factories are lazy (no imports at module level) to avoid loading
# boto3/openai/etc when the provider isn't used.
# Factories accept **kwargs to allow provider-specific options (e.g. model).
PROVIDER_REGISTRY: dict[str, Callable[..., TTSProvider]] = {}


def _register_polly(**kwargs: str | None) -> TTSProvider:
    from langlearn_tts.providers.polly import PollyProvider

    return PollyProvider()


def _register_openai(**kwargs: str | None) -> TTSProvider:
    from langlearn_tts.providers.openai import OpenAIProvider

    model = kwargs.get("model")
    return OpenAIProvider(model=model)


PROVIDER_REGISTRY["polly"] = _register_polly
PROVIDER_REGISTRY["openai"] = _register_openai


def auto_detect_provider() -> str:
    """Detect the provider from environment.

    Checks LANGLEARN_TTS_PROVIDER env var first, otherwise defaults to 'polly'.
    """
    env = os.environ.get("LANGLEARN_TTS_PROVIDER")
    if env:
        return env.lower()
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
    resolved = name.lower() if name is not None else auto_detect_provider()
    factory = PROVIDER_REGISTRY.get(resolved)
    if factory is None:
        available = ", ".join(sorted(PROVIDER_REGISTRY))
        msg = f"Unknown provider '{resolved}'. Available: {available}"
        raise ValueError(msg)
    return factory(**kwargs)
