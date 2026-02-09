"""FastMCP server for langlearn-tts."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from langlearn_tts.core import TTSClient
from langlearn_tts.providers import get_provider
from langlearn_tts.types import (
    MergeStrategy,
    SynthesisRequest,
)

# MCP stdio servers must not write to stdout.
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

mcp = FastMCP("langlearn-tts")


def _validate_voice_settings(
    stability: float | None,
    similarity: float | None,
    style: float | None,
) -> None:
    """Validate ElevenLabs voice settings are in 0.0-1.0 range."""
    for name, value in [
        ("stability", stability),
        ("similarity", similarity),
        ("style", style),
    ]:
        if value is not None and not 0.0 <= value <= 1.0:
            msg = f"{name} must be between 0.0 and 1.0, got {value}"
            raise ValueError(msg)


def _default_output_dir() -> Path:
    """Resolve the default output directory from environment or fallback."""
    env_dir = os.environ.get("LANGLEARN_TTS_OUTPUT_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / "Claude-Audio"


def _resolve_output_dir(output_dir: str | None) -> Path:
    """Resolve an output directory, using the default if not specified."""
    if output_dir:
        return Path(output_dir)
    return _default_output_dir()


def _resolve_output_path(
    output_path: str | None, output_dir: Path, default_name: str
) -> Path:
    """Resolve an output file path."""
    if output_path:
        return Path(output_path)
    return output_dir / default_name


def _play_audio(path: Path) -> None:
    """Play an audio file using macOS afplay (non-blocking).

    Logs a warning and returns silently if afplay is not available
    (e.g. on Linux or Windows).
    """
    try:
        subprocess.Popen(
            ["afplay", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        logger.warning("afplay not found — auto-play requires macOS")


@mcp.tool()
def synthesize(
    text: str,
    voice: str = "joanna",
    rate: int = 90,
    auto_play: bool = True,
    output_path: str | None = None,
    output_dir: str | None = None,
    stability: float | None = None,
    similarity: float | None = None,
    style: float | None = None,
    speaker_boost: bool | None = None,
) -> str:
    """Synthesize text to an MP3 audio file.

    Args:
        text: The text to convert to speech.
        voice: Voice name (e.g. joanna, daniel, lucia, takumi).
            Defaults to joanna.
        rate: Speech rate as percentage (90 = 90% speed, good for
            language learners). Defaults to 90.
        auto_play: Open the file in the default audio player after
            synthesis. Defaults to true.
        output_path: Full path for the output file. If not provided,
            a file is auto-generated in output_dir.
        output_dir: Directory for output. Defaults to LANGLEARN_TTS_OUTPUT_DIR
            env var or ~/Claude-Audio/.
        stability: ElevenLabs voice stability (0.0-1.0). Ignored by
            other providers. Defaults to provider default.
        similarity: ElevenLabs voice similarity boost (0.0-1.0). Ignored
            by other providers. Defaults to provider default.
        style: ElevenLabs voice style/expressiveness (0.0-1.0). Ignored
            by other providers. Defaults to provider default.
        speaker_boost: ElevenLabs speaker boost toggle. Ignored by other
            providers. Defaults to provider default.

    Returns:
        JSON string with file_path, text, and voice fields.
    """
    _validate_voice_settings(stability, similarity, style)
    provider = get_provider()
    provider.resolve_voice(voice)
    request = SynthesisRequest(
        text=text,
        voice=voice,
        rate=rate,
        stability=stability,
        similarity=similarity,
        style=style,
        speaker_boost=speaker_boost,
    )

    dir_path = _resolve_output_dir(output_dir)
    path = _resolve_output_path(
        output_path,
        dir_path,
        f"{voice}_{text[:20].replace(' ', '_')}.mp3",
    )

    client = TTSClient(provider)
    result = client.synthesize(request, path)
    if auto_play:
        _play_audio(result.file_path)
    return str(result.to_dict())


@mcp.tool()
def synthesize_batch(
    texts: list[str],
    voice: str = "joanna",
    rate: int = 90,
    merge: bool = False,
    pause_ms: int = 500,
    auto_play: bool = True,
    output_dir: str | None = None,
    stability: float | None = None,
    similarity: float | None = None,
    style: float | None = None,
    speaker_boost: bool | None = None,
) -> str:
    """Synthesize multiple texts to MP3 files.

    Args:
        texts: List of texts to synthesize.
        voice: Voice name for all texts. Defaults to joanna.
        rate: Speech rate as percentage. Defaults to 90.
        merge: If true, produce one merged file instead of separate
            files per text. Defaults to false.
        pause_ms: Pause between segments in milliseconds when merging.
            Defaults to 500.
        auto_play: Open the file(s) in the default audio player after
            synthesis. Defaults to true.
        output_dir: Directory for output files. Defaults to
            LANGLEARN_TTS_OUTPUT_DIR env var or ~/Claude-Audio/.
        stability: ElevenLabs voice stability (0.0-1.0).
        similarity: ElevenLabs voice similarity boost (0.0-1.0).
        style: ElevenLabs voice style/expressiveness (0.0-1.0).
        speaker_boost: ElevenLabs speaker boost toggle.

    Returns:
        JSON string with list of results, each containing file_path,
        text, and voice fields.
    """
    _validate_voice_settings(stability, similarity, style)
    provider = get_provider()
    provider.resolve_voice(voice)
    requests = [
        SynthesisRequest(
            text=t,
            voice=voice,
            rate=rate,
            stability=stability,
            similarity=similarity,
            style=style,
            speaker_boost=speaker_boost,
        )
        for t in texts
    ]
    strategy = (
        MergeStrategy.ONE_FILE_PER_BATCH if merge else MergeStrategy.ONE_FILE_PER_INPUT
    )
    dir_path = _resolve_output_dir(output_dir)

    client = TTSClient(provider)
    results = client.synthesize_batch(requests, dir_path, strategy, pause_ms)
    if auto_play:
        for r in results:
            _play_audio(r.file_path)
    return str([r.to_dict() for r in results])


@mcp.tool()
def synthesize_pair(
    text1: str,
    text2: str,
    voice1: str = "joanna",
    voice2: str = "hans",
    rate: int = 90,
    pause_ms: int = 500,
    auto_play: bool = True,
    output_path: str | None = None,
    output_dir: str | None = None,
    stability: float | None = None,
    similarity: float | None = None,
    style: float | None = None,
    speaker_boost: bool | None = None,
) -> str:
    """Synthesize a pair of texts and stitch them into one MP3.

    Creates [text1 audio] [pause] [text2 audio]. Use for language
    learning pairs like "strong" (English) + "stark" (German).

    Args:
        text1: First text (typically English).
        text2: Second text (typically target language).
        voice1: Voice for text1. Defaults to joanna (English).
        voice2: Voice for text2. Defaults to hans (German).
        rate: Speech rate as percentage. Defaults to 90.
        pause_ms: Pause between the two texts in milliseconds.
            Defaults to 500.
        auto_play: Play the audio after synthesis. Defaults to true.
        output_path: Full path for the output file.
        output_dir: Directory for output. Defaults to
            LANGLEARN_TTS_OUTPUT_DIR env var or ~/Claude-Audio/.
        stability: ElevenLabs voice stability (0.0-1.0).
        similarity: ElevenLabs voice similarity boost (0.0-1.0).
        style: ElevenLabs voice style/expressiveness (0.0-1.0).
        speaker_boost: ElevenLabs speaker boost toggle.

    Returns:
        JSON string with file_path, text, and voice fields.
    """
    _validate_voice_settings(stability, similarity, style)
    provider = get_provider()
    provider.resolve_voice(voice1)
    provider.resolve_voice(voice2)
    req1 = SynthesisRequest(
        text=text1,
        voice=voice1,
        rate=rate,
        stability=stability,
        similarity=similarity,
        style=style,
        speaker_boost=speaker_boost,
    )
    req2 = SynthesisRequest(
        text=text2,
        voice=voice2,
        rate=rate,
        stability=stability,
        similarity=similarity,
        style=style,
        speaker_boost=speaker_boost,
    )

    dir_path = _resolve_output_dir(output_dir)
    path = _resolve_output_path(
        output_path,
        dir_path,
        f"pair_{text1[:10]}_{text2[:10]}.mp3",
    )

    client = TTSClient(provider)
    result = client.synthesize_pair(text1, req1, text2, req2, path, pause_ms)
    if auto_play:
        _play_audio(result.file_path)
    return str(result.to_dict())


@mcp.tool()
def synthesize_pair_batch(
    pairs: list[list[str]],
    voice1: str = "joanna",
    voice2: str = "hans",
    rate: int = 90,
    pause_ms: int = 500,
    merge: bool = False,
    auto_play: bool = True,
    output_dir: str | None = None,
    stability: float | None = None,
    similarity: float | None = None,
    style: float | None = None,
    speaker_boost: bool | None = None,
) -> str:
    """Synthesize multiple text pairs and stitch each into MP3 files.

    Each pair becomes [text1 audio] [pause] [text2 audio]. Use for
    vocabulary lists like [["strong","stark"], ["house","Haus"]].

    Args:
        pairs: List of [text1, text2] pairs.
        voice1: Voice for all first texts. Defaults to joanna.
        voice2: Voice for all second texts. Defaults to hans.
        rate: Speech rate as percentage. Defaults to 90.
        pause_ms: Pause between pair segments in milliseconds.
            Defaults to 500.
        merge: If true, produce one merged file instead of separate
            files per pair. Defaults to false.
        auto_play: Play the audio after synthesis. Defaults to true.
        output_dir: Directory for output files. Defaults to
            LANGLEARN_TTS_OUTPUT_DIR env var or ~/Claude-Audio/.
        stability: ElevenLabs voice stability (0.0-1.0).
        similarity: ElevenLabs voice similarity boost (0.0-1.0).
        style: ElevenLabs voice style/expressiveness (0.0-1.0).
        speaker_boost: ElevenLabs speaker boost toggle.

    Returns:
        JSON string with list of results.
    """
    _validate_voice_settings(stability, similarity, style)
    provider = get_provider()
    provider.resolve_voice(voice1)
    provider.resolve_voice(voice2)

    pair_requests: list[tuple[SynthesisRequest, SynthesisRequest]] = [
        (
            SynthesisRequest(
                text=p[0],
                voice=voice1,
                rate=rate,
                stability=stability,
                similarity=similarity,
                style=style,
                speaker_boost=speaker_boost,
            ),
            SynthesisRequest(
                text=p[1],
                voice=voice2,
                rate=rate,
                stability=stability,
                similarity=similarity,
                style=style,
                speaker_boost=speaker_boost,
            ),
        )
        for p in pairs
    ]

    strategy = (
        MergeStrategy.ONE_FILE_PER_BATCH if merge else MergeStrategy.ONE_FILE_PER_INPUT
    )
    dir_path = _resolve_output_dir(output_dir)

    client = TTSClient(provider)
    results = client.synthesize_pair_batch(pair_requests, dir_path, strategy, pause_ms)
    if auto_play:
        for r in results:
            _play_audio(r.file_path)
    return str([r.to_dict() for r in results])


def run_server() -> None:
    """Run the MCP server with stdio transport."""
    logger.info("Starting langlearn-tts MCP server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
