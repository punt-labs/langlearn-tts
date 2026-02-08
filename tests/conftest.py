"""Shared test fixtures for langlearn-tts."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydub import AudioSegment

from langlearn_tts.core import PollyClient
from langlearn_tts.types import VoiceConfig

# Test voice configs — constructed directly, no API call needed.
JOANNA = VoiceConfig(voice_id="Joanna", language_code="en-US", engine="neural")
HANS = VoiceConfig(voice_id="Hans", language_code="de-DE", engine="standard")
TATYANA = VoiceConfig(voice_id="Tatyana", language_code="ru-RU", engine="standard")
SEOYEON = VoiceConfig(voice_id="Seoyeon", language_code="ko-KR", engine="neural")


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Provide a temporary output directory."""
    out = tmp_path / "output"
    out.mkdir()
    return out


def _generate_valid_mp3_bytes() -> bytes:
    """Generate minimal valid MP3 bytes using pydub."""
    silence = AudioSegment.silent(duration=50)
    buf = io.BytesIO()
    silence.export(buf, format="mp3")  # pyright: ignore[reportUnknownMemberType]
    return buf.getvalue()


# Cache to avoid regenerating on every call.
_VALID_MP3_BYTES: bytes | None = None


def _get_valid_mp3_bytes() -> bytes:
    global _VALID_MP3_BYTES
    if _VALID_MP3_BYTES is None:
        _VALID_MP3_BYTES = _generate_valid_mp3_bytes()  # pyright: ignore[reportConstantRedefinition]
    return _VALID_MP3_BYTES


def _make_polly_response() -> dict[str, Any]:
    """Create a mock Polly synthesize_speech response with valid MP3."""
    stream = MagicMock()
    stream.read.return_value = _get_valid_mp3_bytes()
    return {
        "AudioStream": stream,
        "ContentType": "audio/mpeg",
        "RequestCharacters": 10,
    }


@pytest.fixture
def mock_boto_client() -> MagicMock:
    """Create a mock boto3 Polly client that returns valid MP3 bytes."""
    client = MagicMock()
    client.synthesize_speech.side_effect = lambda **kwargs: _make_polly_response()  # pyright: ignore[reportUnknownLambdaType]
    return client


@pytest.fixture
def polly_client(mock_boto_client: MagicMock) -> PollyClient:
    """Create a PollyClient with a mocked boto3 backend."""
    return PollyClient(boto_client=mock_boto_client)


@pytest.fixture
def english_voice() -> VoiceConfig:
    return JOANNA


@pytest.fixture
def german_voice() -> VoiceConfig:
    return HANS
