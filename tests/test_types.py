"""Tests for langlearn_tts.types."""

from __future__ import annotations

from pathlib import Path

import pytest

from langlearn_tts.types import (
    HealthCheck,
    MergeStrategy,
    SynthesisRequest,
    SynthesisResult,
    generate_filename,
)


class TestHealthCheck:
    def test_defaults_to_required(self) -> None:
        check = HealthCheck(passed=True, message="ok")
        assert check.required is True

    def test_optional_check(self) -> None:
        check = HealthCheck(passed=False, message="fail", required=False)
        assert check.required is False

    def test_frozen(self) -> None:
        check = HealthCheck(passed=True, message="ok")
        with pytest.raises(AttributeError):
            check.passed = False  # type: ignore[misc]


class TestMergeStrategy:
    def test_separate_value(self) -> None:
        assert MergeStrategy.ONE_FILE_PER_INPUT.value == "separate"

    def test_single_value(self) -> None:
        assert MergeStrategy.ONE_FILE_PER_BATCH.value == "single"


class TestSynthesisRequest:
    def test_default_rate(self) -> None:
        req = SynthesisRequest(text="hello", voice="joanna")
        assert req.rate == 90

    def test_custom_rate(self) -> None:
        req = SynthesisRequest(text="hello", voice="joanna", rate=100)
        assert req.rate == 100

    def test_frozen(self) -> None:
        req = SynthesisRequest(text="hello", voice="joanna")
        with pytest.raises(AttributeError):
            req.text = "world"  # type: ignore[misc]

    def test_voice_is_string(self) -> None:
        req = SynthesisRequest(text="hello", voice="hans")
        assert req.voice == "hans"


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
