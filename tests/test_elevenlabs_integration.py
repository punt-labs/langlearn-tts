"""ElevenLabs integration tests — requires ELEVENLABS_API_KEY.

Run with: uv run pytest tests/test_elevenlabs_integration.py -v -m integration
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from langlearn_tts.providers.elevenlabs import ElevenLabsProvider
from langlearn_tts.types import SynthesisRequest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("ELEVENLABS_API_KEY"),
        reason="ELEVENLABS_API_KEY not set",
    ),
]


@pytest.fixture(scope="module")
def _live_voice() -> tuple[str, str]:  # pyright: ignore[reportUnusedFunction]
    """Fetch the first available voice (short_name, voice_id) from the live API."""
    from elevenlabs import ElevenLabs  # pyright: ignore[reportMissingTypeStubs]

    client: Any = ElevenLabs()  # pyright: ignore[reportUnknownVariableType]
    response: Any = client.voices.get_all()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    voice: Any = response.voices[0]  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    full_name: str = voice.name.lower()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    vid: str = voice.voice_id  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    return (full_name.split(" - ", 1)[0], vid)


@pytest.fixture
def voice_name(_live_voice: tuple[str, str]) -> str:
    """Short name of an available voice."""
    return _live_voice[0]


@pytest.fixture
def provider(_live_voice: tuple[str, str]) -> ElevenLabsProvider:
    """Create a real ElevenLabsProvider with the live voice pre-cached."""
    import langlearn_tts.providers.elevenlabs as elevenlabs

    name, vid = _live_voice
    elevenlabs.VOICES[name] = vid
    return ElevenLabsProvider()


class TestCheckHealth:
    def test_check_health_reports_subscription(
        self, provider: ElevenLabsProvider
    ) -> None:
        checks = provider.check_health()

        assert any(c.passed and "API key: set" in c.message for c in checks)
        assert any(c.passed and "subscription" in c.message.lower() for c in checks)


class TestResolveVoice:
    def test_resolve_voice_known_name(
        self,
        provider: ElevenLabsProvider,
        voice_name: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Known voice name resolves via the live API voice list."""
        import langlearn_tts.providers.elevenlabs as elevenlabs

        monkeypatch.setattr(elevenlabs, "VOICES", {})
        monkeypatch.setattr(elevenlabs, "_voices_loaded", False)

        result = provider.resolve_voice(voice_name)
        assert result == voice_name

    def test_resolve_voice_unknown_raises(self, provider: ElevenLabsProvider) -> None:
        with pytest.raises(ValueError, match="Unknown voice"):
            provider.resolve_voice("zzz_nonexistent_voice_zzz")


class TestSynthesize:
    def test_synthesize_short_text(
        self, provider: ElevenLabsProvider, voice_name: str, tmp_path: Path
    ) -> None:
        request = SynthesisRequest(text="Hello, world.", voice=voice_name, rate=100)
        out = tmp_path / "hello.mp3"

        result = provider.synthesize(request, out)

        assert result.file_path == out
        assert result.text == "Hello, world."
        assert result.voice_name == voice_name
        assert out.exists()
        assert out.stat().st_size > 0

    def test_synthesize_non_english(
        self, provider: ElevenLabsProvider, voice_name: str, tmp_path: Path
    ) -> None:
        """German text synthesis."""
        request = SynthesisRequest(
            text="Guten Tag, wie geht es Ihnen?", voice=voice_name, rate=100
        )
        out = tmp_path / "german.mp3"

        result = provider.synthesize(request, out)

        assert out.exists()
        assert out.stat().st_size > 0
        assert result.text == "Guten Tag, wie geht es Ihnen?"

    def test_synthesize_with_voice_settings(
        self, provider: ElevenLabsProvider, voice_name: str, tmp_path: Path
    ) -> None:
        request = SynthesisRequest(
            text="Testing voice settings.",
            voice=voice_name,
            rate=100,
            stability=0.5,
            similarity=0.7,
            style=0.3,
            speaker_boost=True,
        )
        out = tmp_path / "settings.mp3"

        result = provider.synthesize(request, out)

        assert out.exists()
        assert out.stat().st_size > 0
        assert result.voice_name == voice_name
