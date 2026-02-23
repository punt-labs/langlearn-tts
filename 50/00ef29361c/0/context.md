# Session Context

## User Prompts

### Prompt 1

Implement the following plan:

# Fix: Consolidate output directory resolution (lltts-612)

## Context

Audio files write to different directories depending on the code path. Three independent `_default_output_dir()` implementations exist with different fallback behavior:

| Site | Env var check | Fallback |
|------|---------------|----------|
| `server.py:49` | `LANGLEARN_TTS_OUTPUT_DIR` | `~/langlearn-audio` |
| `cli.py:590` | **None** | `~/langlearn-audio` |
| `output.py:18` | `LANGLEARN_TTS_O...

### Prompt 2

request Copilot review.  Make that standard in your workflow.

### Prompt 3

ok check in 2m

