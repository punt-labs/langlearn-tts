"""Click CLI for langlearn-polly."""

from __future__ import annotations

import json
import logging
import platform
import shutil
import sys
from pathlib import Path
from typing import Any, cast

import click

from langlearn_polly.core import PollyClient
from langlearn_polly.types import (
    MergeStrategy,
    SynthesisRequest,
    SynthesisResult,
    resolve_voice,
)

logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def _print_result(result: SynthesisResult) -> None:
    click.echo(f"{result.file_path}")


def _print_results(results: list[SynthesisResult]) -> None:
    for r in results:
        _print_result(r)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
def main(verbose: bool) -> None:
    """langlearn-polly: AWS Polly TTS for language learning."""
    _configure_logging(verbose)


@main.command()
@click.argument("text")
@click.option(
    "--voice",
    default="joanna",
    show_default=True,
    help="Voice name (e.g. joanna, hans, tatyana, seoyeon).",
)
@click.option(
    "--rate",
    default=90,
    show_default=True,
    type=int,
    help="Speech rate as percentage (e.g. 90 = 90%% speed).",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(path_type=Path),
    help="Output file path. Defaults to auto-generated name in pwd.",
)
def synthesize(text: str, voice: str, rate: int, output: Path | None) -> None:
    """Synthesize a single text to an MP3 file."""
    voice_cfg = resolve_voice(voice)
    request = SynthesisRequest(text=text, voice=voice_cfg, rate=rate)

    if output is None:
        output = Path.cwd() / f"{voice}_{text[:20].replace(' ', '_')}.mp3"

    client = PollyClient()
    result = client.synthesize(request, output)
    _print_result(result)


@main.command("synthesize-batch")
@click.option(
    "--voice",
    default="joanna",
    show_default=True,
    help="Voice name for all texts.",
)
@click.option(
    "--rate",
    default=90,
    show_default=True,
    type=int,
    help="Speech rate as percentage.",
)
@click.option(
    "--output-dir",
    "-d",
    default=None,
    type=click.Path(path_type=Path),
    help="Output directory. Defaults to current directory.",
)
@click.option(
    "--merge",
    is_flag=True,
    default=False,
    help="Merge all outputs into a single file.",
)
@click.option(
    "--pause",
    default=500,
    show_default=True,
    type=int,
    help="Pause between segments in ms (used with --merge).",
)
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def synthesize_batch(
    voice: str,
    rate: int,
    output_dir: Path | None,
    merge: bool,
    pause: int,
    input_file: Path,
) -> None:
    """Synthesize a batch of texts from a JSON file.

    INPUT_FILE should contain a JSON array of strings, e.g.:
    ["hello", "world", "good morning"]
    """
    voice_cfg = resolve_voice(voice)
    raw = json.loads(input_file.read_text(encoding="utf-8"))

    if not isinstance(raw, list):
        raise click.BadParameter("INPUT_FILE must contain a JSON array of strings.")

    texts = cast("list[str]", raw)
    requests = [SynthesisRequest(text=t, voice=voice_cfg, rate=rate) for t in texts]
    strategy = (
        MergeStrategy.ONE_FILE_PER_BATCH if merge else MergeStrategy.ONE_FILE_PER_INPUT
    )
    out_dir = output_dir if output_dir is not None else Path.cwd()

    client = PollyClient()
    results = client.synthesize_batch(requests, out_dir, strategy, pause)
    _print_results(results)


@main.command("synthesize-pair")
@click.argument("text1")
@click.argument("text2")
@click.option(
    "--voice1",
    default="joanna",
    show_default=True,
    help="Voice for the first text (typically English).",
)
@click.option(
    "--voice2",
    default="hans",
    show_default=True,
    help="Voice for the second text (typically L2).",
)
@click.option(
    "--rate",
    default=90,
    show_default=True,
    type=int,
    help="Speech rate as percentage.",
)
@click.option(
    "--pause",
    default=500,
    show_default=True,
    type=int,
    help="Pause between the two texts in ms.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(path_type=Path),
    help="Output file path.",
)
def synthesize_pair(
    text1: str,
    text2: str,
    voice1: str,
    voice2: str,
    rate: int,
    pause: int,
    output: Path | None,
) -> None:
    """Synthesize a pair of texts and stitch them with a pause.

    Creates [TEXT1 audio] [pause] [TEXT2 audio] in a single MP3.
    """
    v1 = resolve_voice(voice1)
    v2 = resolve_voice(voice2)
    req1 = SynthesisRequest(text=text1, voice=v1, rate=rate)
    req2 = SynthesisRequest(text=text2, voice=v2, rate=rate)

    if output is None:
        output = Path.cwd() / f"pair_{text1[:10]}_{text2[:10]}.mp3"

    client = PollyClient()
    result = client.synthesize_pair(text1, req1, text2, req2, output, pause)
    _print_result(result)


@main.command("synthesize-pair-batch")
@click.option(
    "--voice1",
    default="joanna",
    show_default=True,
    help="Voice for first texts (typically English).",
)
@click.option(
    "--voice2",
    default="hans",
    show_default=True,
    help="Voice for second texts (typically L2).",
)
@click.option(
    "--rate",
    default=90,
    show_default=True,
    type=int,
    help="Speech rate as percentage.",
)
@click.option(
    "--pause",
    default=500,
    show_default=True,
    type=int,
    help="Pause between pair segments in ms.",
)
@click.option(
    "--output-dir",
    "-d",
    default=None,
    type=click.Path(path_type=Path),
    help="Output directory. Defaults to current directory.",
)
@click.option(
    "--merge",
    is_flag=True,
    default=False,
    help="Merge all pair outputs into a single file.",
)
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def synthesize_pair_batch(
    voice1: str,
    voice2: str,
    rate: int,
    pause: int,
    output_dir: Path | None,
    merge: bool,
    input_file: Path,
) -> None:
    """Synthesize a batch of text pairs from a JSON file.

    INPUT_FILE should contain a JSON array of [text1, text2] pairs:
    [["strong", "stark"], ["house", "Haus"]]
    """
    v1 = resolve_voice(voice1)
    v2 = resolve_voice(voice2)

    raw = json.loads(input_file.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise click.BadParameter(
            "INPUT_FILE must contain a JSON array of [text1, text2] pairs."
        )

    raw_pairs = cast("list[list[str]]", raw)
    pairs: list[tuple[SynthesisRequest, SynthesisRequest]] = [
        (
            SynthesisRequest(text=p[0], voice=v1, rate=rate),
            SynthesisRequest(text=p[1], voice=v2, rate=rate),
        )
        for p in raw_pairs
    ]

    strategy = (
        MergeStrategy.ONE_FILE_PER_BATCH if merge else MergeStrategy.ONE_FILE_PER_INPUT
    )
    out_dir = output_dir if output_dir is not None else Path.cwd()

    client = PollyClient()
    results = client.synthesize_pair_batch(pairs, out_dir, strategy, pause)
    _print_results(results)


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------

_PASS = "✓"
_FAIL = "✗"
_OPTIONAL = "○"


def _claude_desktop_config_path() -> Path:
    """Return the Claude Desktop config file path (macOS only)."""
    return (
        Path.home()
        / "Library"
        / "Application Support"
        / "Claude"
        / "claude_desktop_config.json"
    )


def _default_output_dir() -> Path:
    return Path.home() / "Claude-Audio"


@main.command()
def doctor() -> None:
    """Check system health for langlearn-polly."""
    passed = 0
    failed = 0
    lines: list[str] = []

    def _check(
        symbol: str, message: str, *, required: bool = True
    ) -> None:
        nonlocal passed, failed
        lines.append(f"{symbol} {message}")
        if symbol == _PASS:
            passed += 1
        elif symbol == _FAIL and required:
            failed += 1

    # Python version
    v = sys.version_info
    if v >= (3, 13):
        _check(_PASS, f"Python {v.major}.{v.minor}.{v.micro}")
    else:
        _check(_FAIL, f"Python {v.major}.{v.minor}.{v.micro} (requires 3.13+)")

    # ffmpeg
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        _check(_PASS, f"ffmpeg: {ffmpeg}")
    else:
        _check(_FAIL, "ffmpeg: not found")

    # AWS credentials
    try:
        import boto3

        sts: Any = boto3.client("sts")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        identity: Any = sts.get_caller_identity()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        account: str = identity["Account"]  # pyright: ignore[reportUnknownVariableType]
        _check(_PASS, f"AWS credentials (account: {account})")
    except Exception:
        _check(_FAIL, "AWS credentials: not configured or invalid")

    # AWS Polly access
    try:
        import boto3 as _boto3

        polly: Any = _boto3.client("polly")  # pyright: ignore[reportUnknownMemberType]
        polly.describe_voices(MaxResults=1)
        _check(_PASS, "AWS Polly access")
    except Exception:
        _check(_FAIL, "AWS Polly access: denied or unavailable")

    # uvx (optional)
    uvx = shutil.which("uvx")
    if uvx:
        _check(_PASS, f"uvx: {uvx}", required=False)
    else:
        _check(_OPTIONAL, "uvx: not found (needed for MCP server)", required=False)

    # Claude Desktop config (optional)
    config_path = _claude_desktop_config_path()
    if config_path.exists():
        _check(_PASS, f"Claude Desktop config: {config_path}", required=False)

        # MCP server registered (optional)
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            servers = data.get("mcpServers", {})
            if "langlearn-polly" in servers:
                _check(
                    _PASS,
                    "MCP server: registered",
                    required=False,
                )
            else:
                _check(
                    _OPTIONAL,
                    "MCP server: not registered (run 'langlearn-polly install')",
                    required=False,
                )
        except (json.JSONDecodeError, OSError):
            _check(
                _OPTIONAL,
                "MCP server: could not read config",
                required=False,
            )
    else:
        _check(_OPTIONAL, "Claude Desktop config: not found", required=False)
        _check(
            _OPTIONAL,
            "MCP server: not registered (run 'langlearn-polly install')",
            required=False,
        )

    # Output directory
    out_dir = _default_output_dir()
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        test_file = out_dir / ".doctor_test"
        test_file.write_text("ok")
        test_file.unlink()
        _check(_PASS, f"Output directory: {out_dir}")
    except OSError as e:
        _check(_FAIL, f"Output directory: {out_dir} ({e})")

    # Print report
    click.echo("=" * 40)
    for line in lines:
        click.echo(line)
    click.echo("=" * 40)
    click.echo(f"{passed} passed, {failed} failed")

    if failed > 0:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------


@main.command()
@click.option(
    "--output-dir",
    default=None,
    type=click.Path(path_type=Path),
    help="Output directory for synthesized audio. Default: ~/Claude-Audio",
)
@click.option(
    "--uvx-path",
    default=None,
    help="Path to uvx binary. Default: auto-detect via shutil.which.",
)
def install(output_dir: Path | None, uvx_path: str | None) -> None:
    """Register the MCP server with Claude Desktop."""
    if platform.system() != "Darwin":
        click.echo(
            "Warning: Claude Desktop config path is only known for macOS. "
            "You may need to configure manually on this platform.",
            err=True,
        )

    # Resolve uvx
    uvx = uvx_path or shutil.which("uvx")
    if not uvx:
        raise click.ClickException(
            "uvx not found. Install uv (https://docs.astral.sh/uv/) first."
        )

    # Resolve output directory
    audio_dir = output_dir or _default_output_dir()
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Read or create config
    config_path = _claude_desktop_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise click.ClickException(
                f"Could not read {config_path}: {e}"
            ) from e
    else:
        data = {}

    if "mcpServers" not in data:
        data["mcpServers"] = {}

    overwriting = "langlearn-polly" in data["mcpServers"]

    data["mcpServers"]["langlearn-polly"] = {
        "command": uvx,
        "args": ["langlearn-polly-server"],
        "env": {
            "POLLY_OUTPUT_DIR": str(audio_dir),
        },
    }

    config_path.write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )

    if overwriting:
        click.echo("Updated existing langlearn-polly entry.")
    else:
        click.echo("Registered langlearn-polly MCP server.")

    click.echo(f"Config: {config_path}")
    click.echo(f"Output: {audio_dir}")
    click.echo("Restart Claude Desktop to activate.")
