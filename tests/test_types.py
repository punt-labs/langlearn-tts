"""Tests for langlearn_tts.types."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from langlearn_tts.types import (
    MergeStrategy,
    SynthesisRequest,
    SynthesisResult,
    VoiceConfig,
    _best_engine,  # pyright: ignore[reportPrivateUsage]
    generate_filename,
    resolve_voice,
)


def _make_describe_voices_response(
    voices: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a mock describe_voices response."""
    return {"Voices": voices}


def _voice_entry(
    voice_id: str,
    language: str,
    engines: list[str],
) -> dict[str, Any]:
    return {
        "Id": voice_id,
        "LanguageCode": language,
        "SupportedEngines": engines,
    }


class TestVoiceConfig:
    def test_voice_config_is_frozen(self) -> None:
        cfg = VoiceConfig(voice_id="Joanna", language_code="en-US", engine="neural")
        with pytest.raises(AttributeError):
            cfg.voice_id = "Matthew"  # type: ignore[misc]


class TestBestEngine:
    def test_prefers_neural(self) -> None:
        assert _best_engine(["standard", "neural"]) == "neural"

    def test_prefers_neural_over_generative(self) -> None:
        assert _best_engine(["generative", "neural", "standard"]) == "neural"

    def test_falls_back_to_generative(self) -> None:
        assert _best_engine(["generative", "long-form"]) == "generative"

    def test_standard_only(self) -> None:
        assert _best_engine(["standard"]) == "standard"


class TestResolveVoice:
    @patch("langlearn_tts.types.boto3")
    def test_resolve_from_api(self, mock_boto3: MagicMock) -> None:
        import langlearn_tts.types as t

        t.VOICES.clear()
        t._voices_loaded = False  # pyright: ignore[reportPrivateUsage]

        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.describe_voices.return_value = _make_describe_voices_response(
            [_voice_entry("Joanna", "en-US", ["neural", "standard"])]
        )

        cfg = resolve_voice("joanna")

        assert cfg.voice_id == "Joanna"
        assert cfg.language_code == "en-US"
        assert cfg.engine == "neural"

    @patch("langlearn_tts.types.boto3")
    def test_resolve_case_insensitive(self, mock_boto3: MagicMock) -> None:
        import langlearn_tts.types as t

        t.VOICES.clear()
        t._voices_loaded = False  # pyright: ignore[reportPrivateUsage]

        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.describe_voices.return_value = _make_describe_voices_response(
            [_voice_entry("Hans", "de-DE", ["standard"])]
        )

        cfg = resolve_voice("HANS")
        assert cfg.voice_id == "Hans"

    @patch("langlearn_tts.types.boto3")
    def test_resolve_unknown_voice_raises(self, mock_boto3: MagicMock) -> None:
        import langlearn_tts.types as t

        t.VOICES.clear()
        t._voices_loaded = False  # pyright: ignore[reportPrivateUsage]

        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.describe_voices.return_value = _make_describe_voices_response([])

        with pytest.raises(ValueError, match="Unknown voice 'nonexistent'"):
            resolve_voice("nonexistent")

    @patch("langlearn_tts.types.boto3")
    def test_caches_api_results(self, mock_boto3: MagicMock) -> None:
        import langlearn_tts.types as t

        t.VOICES.clear()
        t._voices_loaded = False  # pyright: ignore[reportPrivateUsage]

        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.describe_voices.return_value = _make_describe_voices_response(
            [_voice_entry("Lucia", "es-ES", ["neural", "standard"])]
        )

        resolve_voice("lucia")
        resolve_voice("lucia")

        mock_client.describe_voices.assert_called_once()

    def test_uses_cached_voice(self) -> None:
        import langlearn_tts.types as t

        t.VOICES["joanna"] = VoiceConfig(
            voice_id="Joanna", language_code="en-US", engine="neural"
        )
        try:
            cfg = resolve_voice("joanna")
            assert cfg.voice_id == "Joanna"
        finally:
            del t.VOICES["joanna"]


class TestMergeStrategy:
    def test_separate_value(self) -> None:
        assert MergeStrategy.ONE_FILE_PER_INPUT.value == "separate"

    def test_single_value(self) -> None:
        assert MergeStrategy.ONE_FILE_PER_BATCH.value == "single"


class TestSynthesisRequest:
    def test_default_rate(self) -> None:
        cfg = VoiceConfig(voice_id="Joanna", language_code="en-US", engine="neural")
        req = SynthesisRequest(text="hello", voice=cfg)
        assert req.rate == 90

    def test_custom_rate(self) -> None:
        cfg = VoiceConfig(voice_id="Joanna", language_code="en-US", engine="neural")
        req = SynthesisRequest(text="hello", voice=cfg, rate=100)
        assert req.rate == 100

    def test_frozen(self) -> None:
        cfg = VoiceConfig(voice_id="Joanna", language_code="en-US", engine="neural")
        req = SynthesisRequest(text="hello", voice=cfg)
        with pytest.raises(AttributeError):
            req.text = "world"  # type: ignore[misc]


class TestSynthesisResult:
    def test_to_dict(self) -> None:
        result = SynthesisResult(
            file_path=Path("/tmp/test.mp3"),
            text="hello",
            voice_name="Joanna",
        )
        d = result.to_dict()
        assert d["file_path"] == "/tmp/test.mp3"
        assert d["text"] == "hello"
        assert d["voice"] == "Joanna"


class TestGenerateFilename:
    def test_deterministic(self) -> None:
        name1 = generate_filename("hello")
        name2 = generate_filename("hello")
        assert name1 == name2

    def test_different_text_different_name(self) -> None:
        name1 = generate_filename("hello")
        name2 = generate_filename("world")
        assert name1 != name2

    def test_ends_with_mp3(self) -> None:
        name = generate_filename("test")
        assert name.endswith(".mp3")

    def test_prefix(self) -> None:
        name = generate_filename("test", prefix="pair_")
        assert name.startswith("pair_")
        assert name.endswith(".mp3")

    def test_no_prefix(self) -> None:
        name = generate_filename("test")
        assert not name.startswith("pair_")
