"""Click CLI for langlearn-tts."""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast

import click

from langlearn_tts.core import TTSClient
from langlearn_tts.providers import DEFAULT_VOICES, auto_detect_provider, get_provider
from langlearn_tts.types import (
    MergeStrategy,
    SynthesisRequest,
    SynthesisResult,
    TTSProvider,
)

logger = logging.getLogger(__name__)

_PROVIDER_DISPLAY = {"elevenlabs": "ElevenLabs", "polly": "Polly", "openai": "OpenAI"}
_VOICE_DEFAULTS = ", ".join(
    f"{DEFAULT_VOICES[k]} ({_PROVIDER_DISPLAY[k]})"
    for k in ("elevenlabs", "polly", "openai")
)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )
    # Suppress noisy library loggers even in verbose mode
    for name in ("boto3", "botocore", "urllib3", "s3transfer"):
        logging.getLogger(name).setLevel(logging.WARNING)


def _print_result(result: SynthesisResult) -> None:
    click.echo(f"{result.file_path}")


def _print_results(results: list[SynthesisResult]) -> None:
    for r in results:
        _print_result(r)


def _get_provider(ctx: click.Context) -> TTSProvider:
    """Retrieve the TTSProvider from the Click context."""
    obj = cast("dict[str, TTSProvider]", ctx.ensure_object(dict))  # pyright: ignore[reportUnknownMemberType]
    return obj["provider"]


def _voice_settings_options[F: Callable[..., object]](fn: F) -> F:
    """Shared ElevenLabs voice-settings options for synthesis commands."""
    for decorator in reversed(
        [
            click.option(
                "--stability",
                default=None,
                type=click.FloatRange(0.0, 1.0),
                help="ElevenLabs voice stability (0.0-1.0).",
            ),
            click.option(
                "--similarity",
                default=None,
                type=click.FloatRange(0.0, 1.0),
                help="ElevenLabs voice similarity boost (0.0-1.0).",
            ),
            click.option(
                "--style",
                default=None,
                type=click.FloatRange(0.0, 1.0),
                help="ElevenLabs voice style/expressiveness (0.0-1.0).",
            ),
            click.option(
                "--speaker-boost",
                is_flag=True,
                default=False,
                help="Enable ElevenLabs speaker boost.",
            ),
        ]
    ):
        fn = decorator(fn)  # pyright: ignore[reportAssignmentType]
    return fn


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
@click.option(
    "--provider",
    "provider_name",
    default=None,
    envvar="LANGLEARN_TTS_PROVIDER",
    help="TTS provider (elevenlabs, polly, openai). Default: auto-detect.",
)
@click.option(
    "--model",
    default=None,
    envvar="LANGLEARN_TTS_MODEL",
    help="Model name (e.g. eleven_v3, tts-1, tts-1-hd). Provider-specific.",
)
@click.pass_context
def main(
    ctx: click.Context, verbose: bool, provider_name: str | None, model: str | None
) -> None:
    """langlearn-tts: Text-to-speech for language learning."""
    _configure_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["provider"] = get_provider(provider_name, model=model)


@main.command()
@click.argument("text")
@click.option(
    "--voice",
    default=None,
    help=f"Voice name. Default: {_VOICE_DEFAULTS}.",
)
@click.option(
    "--rate",
    default=90,
    show_default=True,
    type=int,
    help="Speech rate as percentage (e.g. 90 = 90%% speed). ElevenLabs ignores this.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(path_type=Path),
    help="Output file path. Defaults to auto-generated name in pwd.",
)
@_voice_settings_options
@click.pass_context
def synthesize(
    ctx: click.Context,
    text: str,
    voice: str | None,
    rate: int,
    output: Path | None,
    stability: float | None,
    similarity: float | None,
    style: float | None,
    speaker_boost: bool,
) -> None:
    """Synthesize a single text to an MP3 file.

    With ElevenLabs eleven_v3, embed audio tags like [tired], [excited],
    [whisper], [laughs] to control delivery.
    """
    provider = _get_provider(ctx)
    voice = voice or provider.default_voice
    provider.resolve_voice(voice)
    request = SynthesisRequest(
        text=text,
        voice=voice,
        rate=rate,
        stability=stability,
        similarity=similarity,
        style=style,
        speaker_boost=speaker_boost if speaker_boost else None,
    )

    if output is None:
        output = Path.cwd() / f"{voice}_{text[:20].replace(' ', '_')}.mp3"

    client = TTSClient(provider)
    result = client.synthesize(request, output)
    _print_result(result)


@main.command("synthesize-batch")
@click.option(
    "--voice",
    default=None,
    help=(f"Voice name for all texts. Default: {_VOICE_DEFAULTS}."),
)
@click.option(
    "--rate",
    default=90,
    show_default=True,
    type=int,
    help="Speech rate as percentage. ElevenLabs ignores this.",
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
@_voice_settings_options
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def synthesize_batch(
    ctx: click.Context,
    voice: str | None,
    rate: int,
    output_dir: Path | None,
    merge: bool,
    pause: int,
    stability: float | None,
    similarity: float | None,
    style: float | None,
    speaker_boost: bool,
    input_file: Path,
) -> None:
    """Synthesize a batch of texts from a JSON file.

    INPUT_FILE should contain a JSON array of strings, e.g.:
    ["hello", "world", "good morning"]
    """
    provider = _get_provider(ctx)
    try:
        raw = json.loads(input_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise click.BadParameter(
            "INPUT_FILE must contain valid JSON (array of strings)."
        ) from exc

    if not isinstance(raw, list):
        raise click.BadParameter("INPUT_FILE must contain a JSON array of strings.")

    for i, item in enumerate(raw):  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
        if not isinstance(item, str):
            raise click.BadParameter(
                f"Element {i} must be a string, got {type(item).__name__}."  # pyright: ignore[reportUnknownArgumentType]
            )

    voice = voice or provider.default_voice
    provider.resolve_voice(voice)
    texts = cast("list[str]", raw)
    boost = speaker_boost if speaker_boost else None
    requests = [
        SynthesisRequest(
            text=t,
            voice=voice,
            rate=rate,
            stability=stability,
            similarity=similarity,
            style=style,
            speaker_boost=boost,
        )
        for t in texts
    ]
    strategy = (
        MergeStrategy.ONE_FILE_PER_BATCH if merge else MergeStrategy.ONE_FILE_PER_INPUT
    )
    out_dir = output_dir if output_dir is not None else Path.cwd()

    client = TTSClient(provider)
    results = client.synthesize_batch(requests, out_dir, strategy, pause)
    _print_results(results)


@main.command("synthesize-pair")
@click.argument("text1")
@click.argument("text2")
@click.option(
    "--voice1",
    default=None,
    help="Voice for first text (typically English). Default: provider's default voice.",
)
@click.option(
    "--voice2",
    default=None,
    help="Voice for the second text (typically L2). Default: provider's default voice.",
)
@click.option(
    "--rate",
    default=90,
    show_default=True,
    type=int,
    help="Speech rate as percentage. ElevenLabs ignores this.",
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
@_voice_settings_options
@click.pass_context
def synthesize_pair(
    ctx: click.Context,
    text1: str,
    text2: str,
    voice1: str | None,
    voice2: str | None,
    rate: int,
    pause: int,
    output: Path | None,
    stability: float | None,
    similarity: float | None,
    style: float | None,
    speaker_boost: bool,
) -> None:
    """Synthesize a pair of texts and stitch them with a pause.

    Creates [TEXT1 audio] [pause] [TEXT2 audio] in a single MP3.
    """
    provider = _get_provider(ctx)
    voice1 = voice1 or provider.default_voice
    voice2 = voice2 or provider.default_voice
    provider.resolve_voice(voice1)
    provider.resolve_voice(voice2)
    boost = speaker_boost if speaker_boost else None
    req1 = SynthesisRequest(
        text=text1,
        voice=voice1,
        rate=rate,
        stability=stability,
        similarity=similarity,
        style=style,
        speaker_boost=boost,
    )
    req2 = SynthesisRequest(
        text=text2,
        voice=voice2,
        rate=rate,
        stability=stability,
        similarity=similarity,
        style=style,
        speaker_boost=boost,
    )

    if output is None:
        output = Path.cwd() / f"pair_{text1[:10]}_{text2[:10]}.mp3"

    client = TTSClient(provider)
    result = client.synthesize_pair(text1, req1, text2, req2, output, pause)
    _print_result(result)


@main.command("synthesize-pair-batch")
@click.option(
    "--voice1",
    default=None,
    help=(
        "Voice for first texts (typically English). Default: provider's default voice."
    ),
)
@click.option(
    "--voice2",
    default=None,
    help="Voice for second texts (typically L2). Default: provider's default voice.",
)
@click.option(
    "--rate",
    default=90,
    show_default=True,
    type=int,
    help="Speech rate as percentage. ElevenLabs ignores this.",
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
@_voice_settings_options
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def synthesize_pair_batch(
    ctx: click.Context,
    voice1: str | None,
    voice2: str | None,
    rate: int,
    pause: int,
    output_dir: Path | None,
    merge: bool,
    stability: float | None,
    similarity: float | None,
    style: float | None,
    speaker_boost: bool,
    input_file: Path,
) -> None:
    """Synthesize a batch of text pairs from a JSON file.

    INPUT_FILE should contain a JSON array of [text1, text2] pairs:
    [["strong", "stark"], ["house", "Haus"]]
    """
    provider = _get_provider(ctx)
    try:
        raw = json.loads(input_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise click.BadParameter(
            "INPUT_FILE must contain valid JSON (array of [text1, text2] pairs)."
        ) from exc
    if not isinstance(raw, list):
        raise click.BadParameter(
            "INPUT_FILE must contain a JSON array of [text1, text2] pairs."
        )

    for i, item in enumerate(raw):  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
        if not isinstance(item, list) or len(item) != 2:  # pyright: ignore[reportUnknownArgumentType]
            raise click.BadParameter(
                f"Element {i} must be a [text1, text2] pair, got {item!r}."
            )
        if not isinstance(item[0], str) or not isinstance(item[1], str):
            raise click.BadParameter(f"Element {i} must contain strings, got {item!r}.")

    voice1 = voice1 or provider.default_voice
    voice2 = voice2 or provider.default_voice
    provider.resolve_voice(voice1)
    provider.resolve_voice(voice2)
    raw_pairs = cast("list[list[str]]", raw)
    boost = speaker_boost if speaker_boost else None
    pairs: list[tuple[SynthesisRequest, SynthesisRequest]] = [
        (
            SynthesisRequest(
                text=p[0],
                voice=voice1,
                rate=rate,
                stability=stability,
                similarity=similarity,
                style=style,
                speaker_boost=boost,
            ),
            SynthesisRequest(
                text=p[1],
                voice=voice2,
                rate=rate,
                stability=stability,
                similarity=similarity,
                style=style,
                speaker_boost=boost,
            ),
        )
        for p in raw_pairs
    ]

    strategy = (
        MergeStrategy.ONE_FILE_PER_BATCH if merge else MergeStrategy.ONE_FILE_PER_INPUT
    )
    out_dir = output_dir if output_dir is not None else Path.cwd()

    client = TTSClient(provider)
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
    return Path.home() / "langlearn-audio"


@main.command()
@click.pass_context
def doctor(ctx: click.Context) -> None:
    """Check system health for langlearn-tts."""
    provider = _get_provider(ctx)
    passed = 0
    failed = 0
    lines: list[str] = []

    def _check(symbol: str, message: str, *, required: bool = True) -> None:
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

    # Active provider
    _check(_PASS, f"Provider: {provider.name}")

    # ffmpeg
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        _check(_PASS, f"ffmpeg: {ffmpeg}")
    else:
        _check(_FAIL, "ffmpeg: not found")

    # Provider-specific health checks
    for check in provider.check_health():
        symbol = _PASS if check.passed else _FAIL
        _check(symbol, check.message, required=check.required)

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
            if "langlearn-tts" in servers:
                _check(
                    _PASS,
                    "MCP server: registered",
                    required=False,
                )
            else:
                _check(
                    _OPTIONAL,
                    "MCP server: not registered (run 'langlearn-tts install')",
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
            "MCP server: not registered (run 'langlearn-tts install')",
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


def _detect_install_provider(provider_name: str | None) -> str:
    """Detect the provider to configure for install.

    If explicit, use it. Otherwise delegates to auto_detect_provider().
    """
    if provider_name:
        return provider_name.lower()
    return auto_detect_provider()


def _build_install_env(provider: str, audio_dir: Path) -> dict[str, str]:
    """Build the env dict for the MCP server config entry.

    Claude Desktop does not support env var interpolation (``${VAR}``),
    so literal values are written. The API key is required because the
    MCP server subprocess does not inherit the user's shell environment.
    """
    env: dict[str, str] = {
        "LANGLEARN_TTS_PROVIDER": provider,
        "LANGLEARN_TTS_OUTPUT_DIR": str(audio_dir),
    }
    if provider == "elevenlabs":
        key = os.environ.get("ELEVENLABS_API_KEY")
        if not key:
            raise click.ClickException(
                "ELEVENLABS_API_KEY is not set."
                " Export it or use --provider polly/openai."
            )
        env["ELEVENLABS_API_KEY"] = key
    elif provider == "openai":
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise click.ClickException(
                "OPENAI_API_KEY is not set. Export it or use --provider polly."
            )
        env["OPENAI_API_KEY"] = key
    return env


@main.command()
@click.option(
    "--output-dir",
    default=None,
    type=click.Path(path_type=Path),
    help="Output directory for synthesized audio. Default: ~/langlearn-audio",
)
@click.option(
    "--uvx-path",
    default=None,
    help="Path to uvx binary. Default: auto-detect via shutil.which.",
)
@click.option(
    "--provider",
    "install_provider",
    default=None,
    help="TTS provider (elevenlabs, polly, openai). Default: auto-detect.",
)
def install(
    output_dir: Path | None, uvx_path: str | None, install_provider: str | None
) -> None:
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

    # Detect provider and build env
    detected = _detect_install_provider(install_provider)
    env = _build_install_env(detected, audio_dir)

    # Read or create config
    config_path = _claude_desktop_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise click.ClickException(f"Could not read {config_path}: {e}") from e
    else:
        data = {}

    if "mcpServers" not in data:
        data["mcpServers"] = {}

    overwriting = "langlearn-tts" in data["mcpServers"]

    data["mcpServers"]["langlearn-tts"] = {
        "command": uvx,
        "args": ["--from", "langlearn-tts", "langlearn-tts-server"],
        "env": env,
    }

    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    if overwriting:
        click.echo("Updated existing langlearn-tts entry.")
    else:
        click.echo("Registered langlearn-tts MCP server.")

    click.echo(f"Provider: {detected}")
    click.echo(f"Config: {config_path}")
    click.echo(f"Output: {audio_dir}")
    click.echo("Restart Claude Desktop to activate.")


# ---------------------------------------------------------------------------
# prompt
# ---------------------------------------------------------------------------

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _prompt_names() -> list[str]:
    """Return sorted prompt names (without .md extension)."""
    if not _PROMPTS_DIR.is_dir():
        return []
    return sorted(p.stem for p in _PROMPTS_DIR.glob("*.md") if p.name != "README.md")


def _extract_instructions(text: str) -> str:
    """Return the content below the --- separator."""
    parts = text.split("\n---\n", 1)
    if len(parts) == 2:
        return parts[1].strip()
    return text.strip()


@main.group()
def prompt() -> None:
    """Browse AI tutor prompts for Claude Desktop."""


@prompt.command("list")
def prompt_list() -> None:
    """List available AI tutor prompts."""
    names = _prompt_names()
    if not names:
        click.echo("No prompts found.")
        return
    for name in names:
        text = (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
        title = text.split("\n", 1)[0].lstrip("# ").strip()
        click.echo(f"  {name:<40} {title}")


@prompt.command("show")
@click.argument("name")
def prompt_show(name: str) -> None:
    """Print a prompt for pasting into Claude Desktop Project Instructions.

    Pipe to clipboard: langlearn-tts prompt show german-high-school | pbcopy
    """
    names = _prompt_names()
    if name not in names:
        raise click.ClickException(
            f"Unknown prompt: {name}\n"
            "Run 'langlearn-tts prompt list' to see available prompts."
        )
    text = (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    click.echo(_extract_instructions(text))
