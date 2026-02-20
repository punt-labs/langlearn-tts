"""OpenAI TTS integration tests — requires OPENAI_API_KEY.

Run with: uv run pytest tests/test_openai_integration.py -v -m integration
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from langlearn_tts.providers.openai import OpenAIProvider
from langlearn_tts.types import SynthesisRequest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set",
    ),
]


@pytest.fixture
def provider() -> OpenAIProvider:
    """Create a real OpenAIProvider (no mock client)."""
    return OpenAIProvider()


class TestCheckHealth:
    def test_check_health_reports_model_access(self, provider: OpenAIProvider) -> None:
        checks = provider.check_health()

        assert any(c.passed and "API key: set" in c.message for c in checks)
        assert any(c.passed and "model access" in c.message.lower() for c in checks)


class TestResolveVoice:
    def test_resolve_voice_known_name(self, provider: OpenAIProvider) -> None:
        assert provider.resolve_voice("nova") == "nova"

    def test_resolve_voice_unknown_raises(self, provider: OpenAIProvider) -> None:
        with pytest.raises(ValueError, match="Unknown voice"):
            provider.resolve_voice("zzz_nonexistent_voice_zzz")


class TestSynthesize:
    def test_synthesize_short_text(
        self, provider: OpenAIProvider, tmp_path: Path
    ) -> None:
        request = SynthesisRequest(text="Hello, world.", voice="nova", rate=100)
        out = tmp_path / "hello.mp3"

        result = provider.synthesize(request, out)

        assert result.path == out
        assert result.text == "Hello, world."
        assert result.voice == "nova"
        assert out.exists()
        assert out.stat().st_size > 0

    def test_synthesize_non_english(
        self, provider: OpenAIProvider, tmp_path: Path
    ) -> None:
        """German text synthesis."""
        request = SynthesisRequest(
            text="Guten Tag, wie geht es Ihnen?", voice="nova", rate=100
        )
        out = tmp_path / "german.mp3"

        result = provider.synthesize(request, out)

        assert out.exists()
        assert out.stat().st_size > 0
        assert result.text == "Guten Tag, wie geht es Ihnen?"

    def test_synthesize_with_speed(
        self, provider: OpenAIProvider, tmp_path: Path
    ) -> None:
        """Synthesis succeeds when using rate=80."""
        request = SynthesisRequest(text="Testing speed.", voice="nova", rate=80)
        out = tmp_path / "speed.mp3"

        result = provider.synthesize(request, out)

        assert out.exists()
        assert out.stat().st_size > 0
        assert result.voice == "nova"
