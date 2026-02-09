# Changelog

All notable changes to langlearn-tts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `TTSProvider` protocol and `HealthCheck` dataclass in `types.py`
- `providers` package with `PollyProvider`, `get_provider()`, and provider registry
- `--provider` CLI flag and `LANGLEARN_TTS_PROVIDER` env var for provider selection
- `TTSClient` generic orchestrator in `core.py` (replaces `PollyClient`)

### Changed
- `SynthesisRequest.voice` is now `str` (voice name) instead of `VoiceConfig`
- All boto3 usage isolated to `providers/polly.py` — core, CLI, and server are provider-agnostic
- `doctor` command delegates provider-specific checks to `provider.check_health()`

### Removed
- `PollyClient` class from `core.py` (replaced by `TTSClient`)
- `VoiceConfig`, `resolve_voice()`, and voice cache from `types.py` (moved to `providers/polly.py`)

## [0.1.2] - 2026-02-08

### Changed
- Rewrote README Quick Start for novice users (step-by-step from zero)

## [0.1.1] - 2026-02-08

### Fixed
- `install` command now uses `uvx --from langlearn-tts langlearn-tts-server` so Claude Desktop can resolve the package from PyPI

### Changed
- Renamed package from `langlearn-polly` to `langlearn-tts` to support multiple TTS providers
- CLI command renamed from `langlearn-polly` to `langlearn-tts`
- MCP server renamed from `langlearn-polly-server` to `langlearn-tts-server`
- GitHub repo renamed from `langlearn-polly-mcp` to `langlearn-tts-mcp`

## [0.1.0] - 2026-02-08

### Added
- Single text synthesis with configurable voice and speech rate
- Batch synthesis from JSON file with optional merge into single file
- Pair synthesis — stitch two languages with a pause between them
- Pair batch synthesis for vocabulary lists
- MCP server (stdio transport) with all four synthesis tools
- Auto-play via `afplay` on macOS for MCP tools
- `doctor` command — checks Python, ffmpeg, AWS credentials, Polly access, uvx, Claude Desktop config, output directory
- `install` command — registers MCP server with Claude Desktop
- Dynamic voice resolution from AWS Polly API (93 voices, 41 languages)
- Automatic engine selection (neural preferred)
- SSML-based speech rate control
