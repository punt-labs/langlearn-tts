# langlearn-polly

AWS Polly text-to-speech for language learning. Provides both an MCP server (for Claude Desktop) and a CLI with identical functionality.

## Features

- **Single synthesis** — convert text to MP3 in any supported language
- **Batch synthesis** — synthesize multiple texts, optionally merged into one file
- **Pair synthesis** — stitch two languages together: `[English audio] [pause] [L2 audio]`
- **Pair batch** — batch process vocabulary lists as stitched pairs
- **Auto-play** — MCP tools play audio immediately after synthesis via `afplay`
- **Configurable speech rate** — default 90% speed for learner-friendly pacing

## Supported Voices

| Voice | Language | Engine |
|-------|----------|--------|
| joanna | English (US) | neural |
| matthew | English (US) | neural |
| vicki | German | neural |
| daniel | German | neural |
| hans | German | standard |
| marlene | German | standard |
| tatyana | Russian | standard |
| maxim | Russian | standard |
| seoyeon | Korean | neural |

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [ffmpeg](https://ffmpeg.org/) (for audio stitching)
- AWS credentials configured (`~/.aws/credentials` or environment variables)

## Installation

```bash
git clone https://github.com/jmf-pobox/langlearn-polly-mcp.git
cd langlearn-polly-mcp
uv sync
```

## Claude Desktop Setup

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "langlearn-polly": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--directory",
        "/path/to/langlearn-polly-mcp",
        "python",
        "-m",
        "langlearn_polly.server"
      ],
      "env": {
        "POLLY_OUTPUT_DIR": "/path/to/output/directory"
      }
    }
  }
}
```

Replace `/path/to/uv` with the absolute path to your `uv` binary (`which uv`). The `POLLY_OUTPUT_DIR` environment variable sets the default output directory; it falls back to `~/polly-audio/` if unset.

Restart Claude Desktop after editing the config.

## CLI Usage

```bash
# Single synthesis
langlearn-polly synthesize "Guten Morgen" --voice daniel -o morning.mp3

# Custom speech rate
langlearn-polly synthesize "Привет" --voice tatyana --rate 70 -o privet.mp3

# Pair: English + German stitched with a pause
langlearn-polly synthesize-pair "good morning" "Guten Morgen" \
  --voice1 joanna --voice2 daniel -o pair.mp3

# Batch from JSON file (["hello", "world", "good morning"])
langlearn-polly synthesize-batch words.json -d output/

# Batch merged into single file
langlearn-polly synthesize-batch words.json -d output/ --merge --pause 800

# Pair batch from JSON file ([["strong", "stark"], ["house", "Haus"]])
langlearn-polly synthesize-pair-batch pairs.json -d output/
```

## MCP Tools

All four tools are available in Claude Desktop once the server is configured:

| Tool | Description |
|------|-------------|
| `synthesize` | Single text to MP3 |
| `synthesize_batch` | Multiple texts, optionally merged |
| `synthesize_pair` | Two texts stitched with a pause |
| `synthesize_pair_batch` | Multiple pairs, optionally merged |

Each tool accepts `auto_play` (default: true) to play audio immediately after synthesis.

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest tests/ -v

# Linting and formatting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type checking
uv run mypy src/ tests/
uv run pyright src/
```

## License

MIT
