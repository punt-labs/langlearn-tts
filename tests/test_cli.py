"""Tests for langlearn_tts.cli."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner, Result

from langlearn_tts.cli import main
from langlearn_tts.types import MergeStrategy, SynthesisResult


def _mock_synthesize_result(path: Path, text: str = "hello") -> SynthesisResult:
    return SynthesisResult(
        file_path=path,
        text=text,
        voice_name="Joanna",
    )


class TestSynthesizeCommand:
    @patch("langlearn_tts.cli.PollyClient")
    def test_synthesize_basic(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "test.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize.return_value = _mock_synthesize_result(out)

        runner = CliRunner()
        result = runner.invoke(main, ["synthesize", "hello", "-o", str(out)])

        assert result.exit_code == 0
        assert str(out) in result.output
        mock_instance.synthesize.assert_called_once()

    @patch("langlearn_tts.cli.PollyClient")
    def test_synthesize_custom_voice(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "test.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize.return_value = _mock_synthesize_result(out)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["synthesize", "Hallo", "--voice", "hans", "-o", str(out)],
        )

        assert result.exit_code == 0
        call_args = mock_instance.synthesize.call_args
        request = call_args[0][0]
        assert request.voice.voice_id == "Hans"

    @patch("langlearn_tts.cli.PollyClient")
    def test_synthesize_custom_rate(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "test.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize.return_value = _mock_synthesize_result(out)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["synthesize", "hello", "--rate", "100", "-o", str(out)],
        )

        assert result.exit_code == 0
        call_args = mock_instance.synthesize.call_args
        request = call_args[0][0]
        assert request.rate == 100

    def test_synthesize_invalid_voice(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["synthesize", "hello", "--voice", "nonexistent"],
        )
        assert result.exit_code != 0


class TestSynthesizeBatchCommand:
    @patch("langlearn_tts.cli.PollyClient")
    def test_batch_basic(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(["hello", "world"]))
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        mock_instance = mock_cls.return_value
        mock_instance.synthesize_batch.return_value = [
            _mock_synthesize_result(out_dir / "a.mp3", "hello"),
            _mock_synthesize_result(out_dir / "b.mp3", "world"),
        ]

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["synthesize-batch", str(input_file), "-d", str(out_dir)],
        )

        assert result.exit_code == 0
        mock_instance.synthesize_batch.assert_called_once()

    @patch("langlearn_tts.cli.PollyClient")
    def test_batch_with_merge(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(["hello", "world"]))
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        mock_instance = mock_cls.return_value
        mock_instance.synthesize_batch.return_value = [
            _mock_synthesize_result(out_dir / "merged.mp3", "hello | world"),
        ]

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "synthesize-batch",
                str(input_file),
                "-d",
                str(out_dir),
                "--merge",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_instance.synthesize_batch.call_args
        assert call_args[0][2] == MergeStrategy.ONE_FILE_PER_BATCH


class TestSynthesizePairCommand:
    @patch("langlearn_tts.cli.PollyClient")
    def test_pair_basic(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "pair.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize_pair.return_value = SynthesisResult(
            file_path=out,
            text="strong | stark",
            voice_name="Joanna+Hans",
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "synthesize-pair",
                "strong",
                "stark",
                "--voice1",
                "joanna",
                "--voice2",
                "hans",
                "-o",
                str(out),
            ],
        )

        assert result.exit_code == 0
        assert str(out) in result.output

    @patch("langlearn_tts.cli.PollyClient")
    def test_pair_custom_pause(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "pair.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize_pair.return_value = SynthesisResult(
            file_path=out,
            text="strong | stark",
            voice_name="Joanna+Hans",
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "synthesize-pair",
                "strong",
                "stark",
                "--pause",
                "1000",
                "-o",
                str(out),
            ],
        )

        assert result.exit_code == 0
        call_args = mock_instance.synthesize_pair.call_args
        # pause is the 6th positional arg
        assert call_args[0][5] == 1000


class TestSynthesizePairBatchCommand:
    @patch("langlearn_tts.cli.PollyClient")
    def test_pair_batch_basic(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        input_file = tmp_path / "pairs.json"
        input_file.write_text(json.dumps([["strong", "stark"], ["house", "Haus"]]))
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        mock_instance = mock_cls.return_value
        mock_instance.synthesize_pair_batch.return_value = [
            SynthesisResult(
                file_path=out_dir / "a.mp3",
                text="strong | stark",
                voice_name="Joanna+Hans",
            ),
            SynthesisResult(
                file_path=out_dir / "b.mp3",
                text="house | Haus",
                voice_name="Joanna+Hans",
            ),
        ]

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "synthesize-pair-batch",
                str(input_file),
                "-d",
                str(out_dir),
            ],
        )

        assert result.exit_code == 0
        mock_instance.synthesize_pair_batch.assert_called_once()


class TestMainGroup:
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "langlearn-tts" in result.output

    def test_synthesize_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["synthesize", "--help"])
        assert result.exit_code == 0
        assert "voice" in result.output.lower()

    def test_verbose_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["-v", "--help"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# doctor tests
# ---------------------------------------------------------------------------


def _mock_boto3_clients(sts_ok: bool = True, polly_ok: bool = True) -> MagicMock:
    """Return a mock for boto3.client that handles 'sts' and 'polly'."""
    mock_sts = MagicMock()
    if sts_ok:
        mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
    else:
        mock_sts.get_caller_identity.side_effect = Exception("no creds")

    mock_polly = MagicMock()
    if polly_ok:
        mock_polly.describe_voices.return_value = {"Voices": []}
    else:
        mock_polly.describe_voices.side_effect = Exception("access denied")

    def client_factory(service: str, **_kwargs: object) -> MagicMock:
        if service == "sts":
            return mock_sts
        if service == "polly":
            return mock_polly
        return MagicMock()

    mock_boto = MagicMock()
    mock_boto.client.side_effect = client_factory
    return mock_boto


class TestDoctorCommand:
    def _run_doctor(
        self,
        tmp_path: Path,
        *,
        sts_ok: bool = True,
        polly_ok: bool = True,
        ffmpeg_found: bool = True,
        uvx_found: bool = True,
        config_exists: bool = False,
        config_data: dict[str, object] | None = None,
    ) -> Result:
        """Invoke doctor with controlled mocks."""
        mock_boto = _mock_boto3_clients(sts_ok=sts_ok, polly_ok=polly_ok)

        def which_side_effect(name: str) -> str | None:
            if name == "ffmpeg" and ffmpeg_found:
                return "/opt/homebrew/bin/ffmpeg"
            if name == "uvx" and uvx_found:
                return "/usr/local/bin/uvx"
            return None

        config_path = tmp_path / "Claude" / "claude_desktop_config.json"
        if config_exists:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(config_data or {}))

        _cli = "langlearn_tts.cli"
        runner = CliRunner()
        with (
            patch(f"{_cli}.shutil.which", side_effect=which_side_effect),
            patch.dict("sys.modules", {"boto3": mock_boto}),
            patch(f"{_cli}._claude_desktop_config_path", return_value=config_path),
            patch(f"{_cli}._default_output_dir", return_value=tmp_path / "audio"),
        ):
            result = runner.invoke(main, ["doctor"])

        return result

    def test_all_required_pass(self, tmp_path: Path) -> None:
        result = self._run_doctor(tmp_path)
        assert result.exit_code == 0
        assert "✓ Python" in result.output
        assert "✓ ffmpeg" in result.output
        assert "✓ AWS credentials" in result.output
        assert "✓ AWS Polly" in result.output
        assert "✓ Output directory" in result.output

    def test_ffmpeg_missing_fails(self, tmp_path: Path) -> None:
        result = self._run_doctor(tmp_path, ffmpeg_found=False)
        assert result.exit_code == 1
        assert "✗ ffmpeg" in result.output

    def test_aws_credentials_fail(self, tmp_path: Path) -> None:
        result = self._run_doctor(tmp_path, sts_ok=False)
        assert result.exit_code == 1
        assert "✗ AWS credentials" in result.output

    def test_polly_access_fail(self, tmp_path: Path) -> None:
        result = self._run_doctor(tmp_path, polly_ok=False)
        assert result.exit_code == 1
        assert "✗ AWS Polly" in result.output

    def test_uvx_missing_is_optional(self, tmp_path: Path) -> None:
        result = self._run_doctor(tmp_path, uvx_found=False)
        # uvx is optional — should not cause failure
        assert result.exit_code == 0
        assert "○ uvx" in result.output

    def test_config_not_found_is_optional(self, tmp_path: Path) -> None:
        result = self._run_doctor(tmp_path, config_exists=False)
        assert result.exit_code == 0
        assert "○ Claude Desktop config" in result.output

    def test_server_registered(self, tmp_path: Path) -> None:
        config_data: dict[str, object] = {
            "mcpServers": {"langlearn-tts": {"command": "uvx"}},
        }
        result = self._run_doctor(
            tmp_path, config_exists=True, config_data=config_data
        )
        assert "✓ MCP server: registered" in result.output

    def test_server_not_registered(self, tmp_path: Path) -> None:
        config_data: dict[str, object] = {"mcpServers": {}}
        result = self._run_doctor(
            tmp_path, config_exists=True, config_data=config_data
        )
        assert "○ MCP server: not registered" in result.output

    def test_summary_counts(self, tmp_path: Path) -> None:
        result = self._run_doctor(tmp_path)
        assert "passed" in result.output
        assert "failed" in result.output


# ---------------------------------------------------------------------------
# install tests
# ---------------------------------------------------------------------------


_CLI = "langlearn_tts.cli"
_UVX = "/usr/local/bin/uvx"


class TestInstallCommand:
    def test_creates_config_from_scratch(self, tmp_path: Path) -> None:
        config_path = tmp_path / "Claude" / "claude_desktop_config.json"
        audio_dir = tmp_path / "audio"

        runner = CliRunner()
        with (
            patch(f"{_CLI}.shutil.which", return_value=_UVX),
            patch(
                f"{_CLI}._claude_desktop_config_path",
                return_value=config_path,
            ),
        ):
            result = runner.invoke(
                main,
                ["install", "--output-dir", str(audio_dir)],
            )

        assert result.exit_code == 0
        assert config_path.exists()

        data = json.loads(config_path.read_text())
        server = data["mcpServers"]["langlearn-tts"]
        assert server["command"] == _UVX
        assert server["args"] == ["langlearn-tts-server"]
        assert server["env"]["POLLY_OUTPUT_DIR"] == str(audio_dir)

    def test_preserves_other_servers(self, tmp_path: Path) -> None:
        config_path = tmp_path / "Claude" / "claude_desktop_config.json"
        config_path.parent.mkdir(parents=True)
        existing: dict[str, object] = {
            "mcpServers": {
                "other-server": {"command": "other", "args": []},
            }
        }
        config_path.write_text(json.dumps(existing))

        runner = CliRunner()
        with (
            patch(f"{_CLI}.shutil.which", return_value=_UVX),
            patch(
                f"{_CLI}._claude_desktop_config_path",
                return_value=config_path,
            ),
        ):
            result = runner.invoke(
                main,
                ["install", "--output-dir", str(tmp_path / "audio")],
            )

        assert result.exit_code == 0
        data = json.loads(config_path.read_text())
        assert "other-server" in data["mcpServers"]
        assert "langlearn-tts" in data["mcpServers"]

    def test_overwrites_existing_entry(self, tmp_path: Path) -> None:
        config_path = tmp_path / "Claude" / "claude_desktop_config.json"
        config_path.parent.mkdir(parents=True)
        existing = {
            "mcpServers": {
                "langlearn-tts": {"command": "old", "args": ["old"]},
            }
        }
        config_path.write_text(json.dumps(existing))

        runner = CliRunner()
        with (
            patch(f"{_CLI}.shutil.which", return_value=_UVX),
            patch(
                f"{_CLI}._claude_desktop_config_path",
                return_value=config_path,
            ),
        ):
            result = runner.invoke(
                main,
                ["install", "--output-dir", str(tmp_path / "audio")],
            )

        assert result.exit_code == 0
        assert "Updated existing" in result.output
        data = json.loads(config_path.read_text())
        server = data["mcpServers"]["langlearn-tts"]
        assert server["command"] == _UVX

    def test_fails_when_uvx_not_found(self, tmp_path: Path) -> None:
        config_path = tmp_path / "Claude" / "claude_desktop_config.json"

        runner = CliRunner()
        with (
            patch(f"{_CLI}.shutil.which", return_value=None),
            patch(
                f"{_CLI}._claude_desktop_config_path",
                return_value=config_path,
            ),
        ):
            result = runner.invoke(
                main,
                ["install", "--output-dir", str(tmp_path / "audio")],
            )

        assert result.exit_code != 0
        assert "uvx not found" in result.output

    def test_custom_uvx_path(self, tmp_path: Path) -> None:
        config_path = tmp_path / "Claude" / "claude_desktop_config.json"

        runner = CliRunner()
        with patch(
            f"{_CLI}._claude_desktop_config_path",
            return_value=config_path,
        ):
            result = runner.invoke(
                main,
                [
                    "install",
                    "--output-dir",
                    str(tmp_path / "audio"),
                    "--uvx-path",
                    "/custom/bin/uvx",
                ],
            )

        assert result.exit_code == 0
        data = json.loads(config_path.read_text())
        server = data["mcpServers"]["langlearn-tts"]
        assert server["command"] == "/custom/bin/uvx"

    def test_creates_output_directory(self, tmp_path: Path) -> None:
        config_path = tmp_path / "Claude" / "claude_desktop_config.json"
        audio_dir = tmp_path / "nested" / "audio"

        runner = CliRunner()
        with (
            patch(f"{_CLI}.shutil.which", return_value=_UVX),
            patch(
                f"{_CLI}._claude_desktop_config_path",
                return_value=config_path,
            ),
        ):
            result = runner.invoke(
                main,
                ["install", "--output-dir", str(audio_dir)],
            )

        assert result.exit_code == 0
        assert audio_dir.is_dir()
