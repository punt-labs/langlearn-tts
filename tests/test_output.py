"""Tests for langlearn_tts.output."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from langlearn_tts.output import default_output_dir, resolve_output_path
from langlearn_tts.types import SynthesisRequest


class TestDefaultOutputDir:
    def test_returns_env_var_when_set(self, tmp_path: Path) -> None:
        custom = str(tmp_path / "custom-audio")
        with patch.dict("os.environ", {"LANGLEARN_TTS_OUTPUT_DIR": custom}):
            result = default_output_dir()
        assert result == Path(custom)

    def test_falls_back_to_home_langlearn_audio(self) -> None:
        with patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("LANGLEARN_TTS_OUTPUT_DIR", None)
            result = default_output_dir()
        assert result == Path.home() / "langlearn-audio"


class TestResolveOutputPath:
    def test_uses_explicit_output_path(self, tmp_path: Path) -> None:
        explicit = tmp_path / "explicit.mp3"
        request = SynthesisRequest(
            text="hello",
            voice="joanna",
            metadata={"output_path": str(explicit)},
        )
        result = resolve_output_path(request)
        assert result == explicit

    def test_uses_output_dir_from_metadata(self, tmp_path: Path) -> None:
        request = SynthesisRequest(
            text="hello",
            voice="joanna",
            metadata={"output_dir": str(tmp_path)},
        )
        result = resolve_output_path(request)
        assert result.parent == tmp_path

    def test_falls_back_to_default_output_dir(self, tmp_path: Path) -> None:
        with patch(
            "langlearn_tts.output.default_output_dir", return_value=tmp_path / "audio"
        ):
            request = SynthesisRequest(text="hello", voice="joanna")
            result = resolve_output_path(request)
        assert result.parent == tmp_path / "audio"
