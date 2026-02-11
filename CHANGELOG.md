# Changelog

All notable changes to langlearn-tts will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Rotating file logging to `~/.langlearn-tts/logs/langlearn-tts.log` (5 MB, 5 backups)
- Timestamps and module names in log format
- API call logging at INFO level: provider name, voice, character count

### Fixed
- Removed request text from Polly debug log (payload leak)

### Changed
- Logging configured via `logging.config.dictConfig()` in shared `logging_config` module

## [0.5.1] - 2026-02-10

### Fixed
- MCP server now reports package version (e.g. `0.5.1`) instead of FastMCP library version in `serverInfo`

## [0.5.0] - 2026-02-10

### Added
- Language-first TTS: language is now a first-class concept across the entire stack
- `--language`/`--lang` option on CLI `synthesize` and `synthesize-batch` commands
- `--lang1`/`--lang2` options on CLI `synthesize-pair` and `synthesize-pair-batch` commands
- `language` parameter on MCP `synthesize` and `synthesize_batch` tools
- `lang1`/`lang2` parameters on MCP `synthesize_pair` and `synthesize_pair_batch` tools
- `language` field on `SynthesisRequest` and `SynthesisResult` types
- `validate_language()` function for ISO 639-1 code validation
- `SUPPORTED_LANGUAGES` reference dictionary (33 languages)
- `TTSProvider` protocol extended with `get_default_voice()`, `list_voices()`, `infer_language_from_voice()`
- Polly: voice-language compatibility validation, language inference from voice, language-filtered voice listing
- Polly: default voice per language (20 languages)
- OpenAI/ElevenLabs: language pass-through (multilingual voices)
- CONTRIBUTING.md with bug reporting, dev setup, quality gates, testing, commit format, and PR workflow
- PyPI keywords (tts, text-to-speech, mcp, language-learning, elevenlabs, aws-polly, openai) and Repository URL
- PyPI classifiers: Education audience, Console environment, Education topic; Development Status bumped to Beta

### Changed
- CLI `--rate` help text notes ElevenLabs ignores the rate parameter
- CLI synthesize docstring documents ElevenLabs audio tags
- CLI and MCP `--voice` help shows concrete defaults per provider (rachel/joanna/nova)
- OpenAI README section expanded with default model, auto-chunking, and per-model pricing
- Voice is now optional when language is provided — the provider selects a default voice for the language

### Fixed
- Polly and OpenAI voice error messages truncated to 10 voices (matching ElevenLabs), down from full list (93 voices for Polly)

## [0.4.4] - 2026-02-09

### Fixed
- Suppress pydub 0.25.1 `SyntaxWarning` on Python 3.13 — invalid escape sequences in pydub's regex strings printed to stderr on first run after install

## [0.4.3] - 2026-02-09

### Changed
- All 28 tutor prompts are now provider-agnostic — removed hardcoded Polly voice names, server auto-selects voices
- Tutor prompts add level-calibrated target language interaction: classroom L2 routines (beginner), circumlocution and rephrasing (intermediate), L2 immersion with English redirect (advanced)

## [0.4.2] - 2026-02-09

### Added
- MCP tool docstrings document ElevenLabs eleven_v3 audio tags — free-form performance cues like `[tired]`, `[excited]`, `[whisper]`, `[sigh]` that control voice delivery

## [0.4.1] - 2026-02-09

### Fixed
- ElevenLabs voice resolution: API returns names with descriptions (e.g. "Adam - dominant, firm"); lookups of short names like "adam" now resolve correctly
- MCP tool voice defaults: replaced hardcoded Polly voice names (`joanna`, `hans`) with provider-aware defaults (`rachel` for ElevenLabs, `joanna` for Polly, `nova` for OpenAI)
- MCP tool docstrings: voice examples are now provider-agnostic so LLM clients pick valid voices
- ElevenLabs health check: ApiError output now shows clean message instead of full HTTP headers
- CLI `--help`: `--provider` and `--model` flags now mention ElevenLabs
- Test isolation: install tests no longer leak `ELEVENLABS_API_KEY` from environment

### Added
- `default_voice` property on `TTSProvider` protocol

## [0.4.0] - 2026-02-09

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
