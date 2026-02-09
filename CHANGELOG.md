# Changelog

All notable changes to langlearn-tts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ElevenLabs TTS provider (`providers/elevenlabs.py`) with 5,000+ voices, 70+ languages, default model `eleven_v3`
- Voice settings: `--stability`, `--similarity`, `--style`, `--speaker-boost` CLI flags and MCP tool params (ElevenLabs only)
- Auto-detection prefers ElevenLabs when `ELEVENLABS_API_KEY` is set
- `install` command supports `--provider elevenlabs` and writes `ELEVENLABS_API_KEY` to config
- `split_text()` public function in `core.py` for provider-agnostic text chunking

### Changed
- Text chunking (`split_text`, `_split_at_words`) moved from `providers/openai.py` to `core.py` for shared use across providers
- `SynthesisRequest` gains optional `stability`, `similarity`, `style`, `speaker_boost` fields (ignored by Polly and OpenAI)

## [0.3.2] - 2026-02-08

### Changed
- Default provider is now Polly (was OpenAI when `OPENAI_API_KEY` was set) — dedicated per-language neural voices produce more native-sounding pronunciation
- OpenAI provider requires explicit opt-in via `--provider openai` or `LANGLEARN_TTS_PROVIDER=openai`

## [0.3.1] - 2026-02-08

### Fixed
- `install` command writes literal `OPENAI_API_KEY` value — Claude Desktop does not support `${VAR}` env var interpolation (that syntax is Claude Code only)

## [0.3.0] - 2026-02-08

### Added
- `TTSProvider` protocol and `HealthCheck` dataclass in `types.py`
- `providers` package with `PollyProvider`, `get_provider()`, and provider registry
- `--provider` CLI flag and `LANGLEARN_TTS_PROVIDER` env var for provider selection
- `TTSClient` generic orchestrator in `core.py` (replaces `PollyClient`)
- OpenAI TTS provider (`providers/openai.py`) with 9 voices (alloy, ash, coral, echo, fable, onyx, nova, sage, shimmer)
- `--model` CLI flag and `LANGLEARN_TTS_MODEL` env var for model selection (e.g. tts-1, tts-1-hd)
- Auto-chunking for OpenAI texts exceeding 4096 characters (sentence then word boundary splitting)
- Auto-detection: defaults to OpenAI when `OPENAI_API_KEY` is set

### Changed
- `install` command auto-detects provider and writes `LANGLEARN_TTS_PROVIDER` + `OPENAI_API_KEY` (when applicable) into Claude Desktop config
- `install` command accepts `--provider` flag to override auto-detection
- `doctor` command shows active provider name
- `SynthesisRequest.voice` is now `str` (voice name) instead of `VoiceConfig`
- All boto3 usage isolated to `providers/polly.py` — core, CLI, and server are provider-agnostic
- `doctor` command delegates provider-specific checks to `provider.check_health()`
- `get_provider()` accepts `**kwargs` for provider-specific options (e.g. `model`)

### Fixed
- OpenAI chunking: `_split_at_words` now character-splits words exceeding `max_chars` instead of emitting oversized chunks

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
