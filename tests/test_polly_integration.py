"""AWS Polly integration tests — requires AWS credentials.

Run with: uv run pytest tests/test_polly_integration.py -v -m integration
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

import langlearn_tts.providers.polly as polly
from langlearn_tts.providers.polly import PollyProvider
from langlearn_tts.types import SynthesisRequest


def _has_aws_credentials() -> bool:
    """Check whether AWS credentials are available via botocore session."""
    import botocore.session  # pyright: ignore[reportMissingTypeStubs]

    session = botocore.session.Session()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    return session.get_credentials() is not None  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnnecessaryComparison]


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _has_aws_credentials(),
        reason="AWS credentials not configured",
    ),
]


@pytest.fixture(autouse=True)
def _reset_voice_cache() -> Iterator[None]:  # pyright: ignore[reportUnusedFunction]
    """Clear the mock voice cache so integration tests hit the real Polly API.

    The conftest autouse fixture sets _voices_loaded=True with 4 mock voices.
    This fixture runs after it and resets the state for each test,
    restoring the previous global state afterwards.
    """
    prev_voices = dict(polly.VOICES)
    prev_loaded = polly._voices_loaded  # pyright: ignore[reportPrivateUsage]

    polly.VOICES.clear()
    polly._voices_loaded = False  # pyright: ignore[reportPrivateUsage]
    try:
        yield
    finally:
        polly.VOICES.clear()
        polly.VOICES.update(prev_voices)
        polly._voices_loaded = prev_loaded  # pyright: ignore[reportPrivateUsage]


@pytest.fixture
def provider() -> PollyProvider:
    """Create a real PollyProvider (no mock boto client)."""
    return PollyProvider()


class TestCheckHealth:
    def test_reports_credentials_and_access(self, provider: PollyProvider) -> None:
        checks = provider.check_health()

        assert any(c.passed and "credentials" in c.message.lower() for c in checks)
        assert any(c.passed and "polly access" in c.message.lower() for c in checks)


class TestResolveVoice:
    def test_known_name(self, provider: PollyProvider) -> None:
        assert provider.resolve_voice("joanna") == "Joanna"

    def test_unknown_raises(self, provider: PollyProvider) -> None:
        with pytest.raises(ValueError, match="Unknown voice"):
            provider.resolve_voice("zzz_nonexistent_voice_zzz")

    def test_with_matching_language(self, provider: PollyProvider) -> None:
        assert provider.resolve_voice("joanna", language="en") == "Joanna"

    def test_with_mismatching_language(self, provider: PollyProvider) -> None:
        with pytest.raises(ValueError, match="does not support language 'de'"):
            provider.resolve_voice("joanna", language="de")


class TestSynthesize:
    def test_short_text(self, provider: PollyProvider, tmp_path: Path) -> None:
        request = SynthesisRequest(text="Hello, world.", voice="joanna", rate=100)
        out = tmp_path / "hello.mp3"

        result = provider.synthesize(request, out)

        assert result.file_path == out
        assert result.text == "Hello, world."
        assert result.voice_name == "Joanna"
        assert out.exists()
        assert out.stat().st_size > 0

    def test_non_english(self, provider: PollyProvider, tmp_path: Path) -> None:
        """German text synthesis with voice="vicki" and language="de"."""
        request = SynthesisRequest(
            text="Guten Tag, wie geht es Ihnen?",
            voice="vicki",
            rate=100,
            language="de",
        )
        out = tmp_path / "german.mp3"

        result = provider.synthesize(request, out)

        assert out.exists()
        assert out.stat().st_size > 0
        assert result.text == "Guten Tag, wie geht es Ihnen?"
        assert result.language == "de"

    def test_rate_applied(self, provider: PollyProvider, tmp_path: Path) -> None:
        """rate=80 produces SSML prosody and valid output."""
        request = SynthesisRequest(text="Slowly now.", voice="joanna", rate=80)
        out = tmp_path / "slow.mp3"

        result = provider.synthesize(request, out)

        assert out.exists()
        assert out.stat().st_size > 0
        assert result.voice_name == "Joanna"


class TestLanguageSupport:
    def test_list_voices_from_api(self, provider: PollyProvider) -> None:
        """list_voices() fetches real voices from the API."""
        voices = provider.list_voices()

        assert len(voices) > 0
        assert voices == sorted(voices)

    def test_list_voices_filtered_by_language(self, provider: PollyProvider) -> None:
        """list_voices('de') returns only German voices."""
        voices = provider.list_voices(language="de")

        assert len(voices) > 0
        assert all(
            (provider.infer_language_from_voice(v) or "").startswith("de")
            for v in voices
        )

    def test_infer_language_from_voice(self, provider: PollyProvider) -> None:
        assert provider.infer_language_from_voice("joanna") == "en"

    def test_get_default_voice(self, provider: PollyProvider) -> None:
        assert provider.get_default_voice("de") == "vicki"
