"""Tests for langlearn_tts.output."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from langlearn_tts.output import default_output_dir, expand_path, resolve_output_path
from langlearn_tts.types import SynthesisRequest


class TestExpand:
    def test_expands_tilde(self) -> None:
        result = expand_path("~/audio")
        assert result == Path.home() / "audio"

    def test_expands_env_var(self, tmp_path: Path) -> None:
        with patch.dict("os.environ", {"MY_DIR": str(tmp_path)}):
            result = expand_path("$MY_DIR/audio")
        assert result == tmp_path / "audio"

    def test_expands_both_tilde_and_var(self, tmp_path: Path) -> None:
        with patch.dict("os.environ", {"SUB": "sub"}):
            result = expand_path("~/$SUB/audio")
        assert result == Path.home() / "sub" / "audio"

    def test_passthrough_absolute_path(self, tmp_path: Path) -> None:
        result = expand_path(str(tmp_path))
        assert result == tmp_path


class TestDefaultOutputDir:
    def test_returns_env_var_when_set(self, tmp_path: Path) -> None:
        custom = str(tmp_path / "custom-audio")
        with patch.dict("os.environ", {"TTS_OUTPUT_DIR": custom}):
            result = default_output_dir()
        assert result == Path(custom)

    def test_expands_tilde_in_env_var(self) -> None:
        with patch.dict("os.environ", {"TTS_OUTPUT_DIR": "~/my-audio"}):
            result = default_output_dir()
        assert result == Path.home() / "my-audio"

    def test_expands_env_var_in_env_var(self, tmp_path: Path) -> None:
        with patch.dict(
            "os.environ",
            {"TTS_OUTPUT_DIR": "$MY_BASE/my-audio", "MY_BASE": str(tmp_path)},
        ):
            result = default_output_dir()
        assert result == tmp_path / "my-audio"

    def test_falls_back_to_home_langlearn_audio(self) -> None:
        with patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("TTS_OUTPUT_DIR", None)
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

    def test_expands_tilde_in_output_path(self) -> None:
        request = SynthesisRequest(
            text="hello",
            voice="joanna",
            metadata={"output_path": "~/audio/test.mp3"},
        )
        with patch("pathlib.Path.mkdir"):
            result = resolve_output_path(request)
        assert result == Path.home() / "audio" / "test.mp3"

    def test_expands_env_var_in_output_dir(self, tmp_path: Path) -> None:
        with patch.dict("os.environ", {"MY_AUDIO": str(tmp_path)}):
            request = SynthesisRequest(
                text="hello",
                voice="joanna",
                metadata={"output_dir": "$MY_AUDIO"},
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
