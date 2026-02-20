# langlearn-tts

[![PyPI](https://img.shields.io/pypi/v/punt-langlearn-tts)](https://pypi.org/project/punt-langlearn-tts/)
[![GitHub](https://img.shields.io/github/v/release/punt-labs/langlearn-tts)](https://github.com/punt-labs/langlearn-tts)
[![Tests](https://github.com/punt-labs/langlearn-tts/actions/workflows/ci.yml/badge.svg)](https://github.com/punt-labs/langlearn-tts/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/punt-langlearn-tts)](https://pypi.org/project/punt-langlearn-tts/)

A Claude Desktop extension that gives Claude the ability to speak. Ask Claude to pronounce words, generate audio flashcards, or run a full language lesson with audio — in 70+ languages.

## Quick Start

### 1. Get a TTS API key

You need an account with at least one text-to-speech provider:

- [**ElevenLabs**](https://elevenlabs.io) — best quality, 70+ languages, 5,000+ voices. Free tier: 10K chars/month. (Recommended)
- [**OpenAI TTS**](https://platform.openai.com/docs/guides/text-to-speech) — good quality, easiest setup, 57 languages, 9 voices.
- [**AWS Polly**](https://aws.amazon.com/polly/) — better quality, 41 languages, 100+ voices, difficult setup ([setup guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)).

### 2. Install in Claude Desktop

[**Download punt-langlearn-tts.mcpb**](https://github.com/punt-labs/langlearn-tts/releases/latest/download/punt-langlearn-tts.mcpb) and double-click to install. Claude Desktop will prompt you for your API key and an output directory.

### 3. Set up a tutor project (optional)

langlearn-tts ships with 28 tutor prompts — one for each combination of 7 languages and 4 levels. Setting up a project gives Claude a tutor persona that generates audio during lessons.

1. In Claude Desktop, click **Projects** in the sidebar
2. Click **Create Project** and name it (e.g., "German with Herr Schmidt")
3. Open the project, click **Set custom instructions**
4. Copy a prompt from the [prompts directory](https://github.com/punt-labs/langlearn-tts/tree/main/src/langlearn_tts/prompts) and paste it into the Instructions field
5. Start a new conversation within that project

| Language | High School | 1st Year | 2nd Year | Advanced |
|----------|-------------|----------|----------|----------|
| German | Herr Schmidt | Professorin Weber | Professor Hartmann | Professor Becker |
| Spanish | Profesora Elena | Profesor Garcia | Profesora Carmen | Profesora Reyes |
| French | Madame Moreau | Professeur Laurent | Professeur Dubois | Professeur Beaumont |
| Russian | Irina Petrovna | Professor Dmitri | Professor Natasha | Professor Mikhail |
| Korean | Kim-seonsaengnim | Professor Park | Professor Kim | Professor Yoon |
| Japanese | Tanaka-sensei | Yamamoto-sensei | Suzuki-sensei | Mori-sensei |
| Chinese | Laoshi Wang | Professor Chen | Professor Zhang | Professor Wei |

Each prompt is calibrated to the student's level, based on [Mollick & Mollick's "Assigning AI" framework](https://ssrn.com/abstract=4475995).

### 4. Try it out

In any Claude Desktop conversation, try:

> "Say 'Guten Morgen' in German"

> "Create an audio flashcard: 'good morning' in English, then 'Guten Morgen' in German"

> "Synthesize these Spanish words as a merged audio file: hola, gracias, por favor, de nada"

> "Generate pair flashcards for these German vocabulary words: strong/stark, house/Haus, book/Buch"

Audio plays automatically after each request. Files are saved to your output directory (`~/langlearn-audio` by default).

## Features

- **Pronounce anything** — ask Claude to say a word or phrase and hear it spoken aloud
- **Audio flashcards** — Claude creates an MP3 with English first, then the target language, with a pause between them
- **Vocabulary lists** — give Claude a list of words and get back individual or merged audio files
- **70+ languages** — German, Spanish, French, Russian, Korean, Japanese, Chinese, and many more
- **Tutor mode** — 28 built-in tutor personas that teach with audio throughout the lesson
- **Multiple voices** — each provider offers a range of voices; ask Claude to use a specific one by name
- **Adjustable speed** — audio defaults to 90% speed so learners can hear pronunciation clearly

## Troubleshooting

If something isn't working, ask Claude to run a health check:

> "Run the doctor command to check if everything is set up correctly"

Logs are written to `~/.langlearn-tts/logs/langlearn-tts.log` (never contains the text you synthesize). See [PRIVACY.md](PRIVACY.md) for details.

---

## Developer Reference

Everything below is for developers using the CLI, integrating with other MCP clients, or contributing to the project.

### CLI Installation

Install [uv](https://docs.astral.sh/uv/) (manages Python automatically), then:

```bash
uv tool install punt-langlearn-tts
```

Install ffmpeg for audio stitching (pairs, merged batches):

```bash
# macOS (requires Homebrew — install from https://brew.sh if needed)
brew install ffmpeg

# Linux — see https://ffmpeg.org/download.html for your distro

# Windows
winget install --id Gyan.FFmpeg
```

Verify:

```bash
langlearn-tts doctor
```

### Claude Desktop setup via CLI

```bash
langlearn-tts install
```

Writes to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS). Options: `--provider NAME`, `--output-dir PATH`, `--uvx-path PATH`. Restart Claude Desktop after running.

Or add manually:

```json
{
  "mcpServers": {
    "langlearn-tts": {
      "command": "/absolute/path/to/uvx",
      "args": ["--from", "punt-langlearn-tts", "langlearn-tts-server"],
      "env": {
        "LANGLEARN_TTS_OUTPUT_DIR": "/absolute/path/to/output/directory"
      }
    }
  }
}
```

Claude Desktop does not inherit your shell environment. API keys must be literal values (env var references are not supported). Restart after editing.

### Environment variables

| Env var | Required | Description |
|---------|----------|-------------|
| `LANGLEARN_TTS_PROVIDER` | No | `elevenlabs`, `polly` (default when no API key), or `openai` |
| `ELEVENLABS_API_KEY` | For ElevenLabs | Your API key |
| `OPENAI_API_KEY` | For OpenAI | Your API key |
| `LANGLEARN_TTS_OUTPUT_DIR` | No | Output directory (default: `~/langlearn-audio`) |
| `LANGLEARN_TTS_MODEL` | No | Model name. ElevenLabs: `eleven_v3` (default). OpenAI: `tts-1`, `tts-1-hd` |

For Polly, AWS credentials are read from `~/.aws/credentials`.

### CLI Usage

```bash
# Single synthesis
langlearn-tts synthesize "Guten Morgen" --voice daniel -o morning.mp3

# Custom speech rate (percentage, default 90)
langlearn-tts synthesize "Привет" --voice tatyana --rate 70 -o privet.mp3

# ElevenLabs with voice settings
langlearn-tts synthesize "Guten Morgen" --voice Rachel \
  --stability 0.5 --similarity 0.7 --style 0.3 --speaker-boost

# Pair: English + German stitched with a pause
langlearn-tts synthesize-pair "good morning" "Guten Morgen" \
  --voice1 joanna --voice2 daniel -o pair.mp3

# Batch from JSON file (["hello", "world", "good morning"])
langlearn-tts synthesize-batch words.json -d output/

# Batch merged into single file
langlearn-tts synthesize-batch words.json -d output/ --merge --pause 800

# Pair batch from JSON file ([["strong", "stark"], ["house", "Haus"]])
langlearn-tts synthesize-pair-batch pairs.json -d output/

# Browse AI tutor prompts
langlearn-tts prompt list
langlearn-tts prompt show german-high-school | pbcopy
```

### Voices

**ElevenLabs** — 5,000+ voices. Any voice works with any language. You can also pass a voice ID directly (the 20-character string from the ElevenLabs dashboard). Voice settings: `--stability`, `--similarity`, `--style` (0.0–1.0), `--speaker-boost` (flag).

**AWS Polly** — 93 voices from the [AWS Polly voice list](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html). Each voice is trained for a specific language. Engine (neural, standard, generative, long-form) is selected automatically.

**OpenAI TTS** — 9 voices: alloy, ash, coral, echo, fable, onyx, nova, sage, shimmer. Default model: `tts-1`. Use `--model tts-1-hd` for higher quality.

All voice names are case-insensitive.

### MCP Tools

| Tool | Description |
|------|-------------|
| `synthesize` | Single text to MP3 |
| `synthesize_batch` | Multiple texts, optionally merged |
| `synthesize_pair` | Two texts stitched with a pause |
| `synthesize_pair_batch` | Multiple pairs, optionally merged |

Each tool accepts `auto_play` (default: true) to play audio immediately after synthesis.

### Other MCP clients

langlearn-tts works with any MCP client that supports stdio transport. Use the server command `uvx --from punt-langlearn-tts langlearn-tts-server` with the environment variables above. Find your `uvx` path with `which uvx` — all paths must be absolute.

### Development

```bash
git clone https://github.com/punt-labs/langlearn-tts.git
cd langlearn-tts
uv sync --all-extras

uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/ tests/
uv run pyright src/ tests/
```

## License

MIT
