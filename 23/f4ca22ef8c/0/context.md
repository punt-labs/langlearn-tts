# Session Context

## User Prompts

### Prompt 1

Implement the following plan:

# Release v0.6.3

## Context

The output directory consolidation fix (PR #29, lltts-612) is merged to main. Users on `0.6.2` may get files written to cwd instead of `~/langlearn-audio`. We need to release `0.6.3` to PyPI and build a new `.mcpb` Desktop Extension bundle.

## Version bump: 0.6.2 → 0.6.3

Three files to update:
- `pyproject.toml:3` — `version = "0.6.2"` → `"0.6.3"`
- `src/langlearn_tts/__init__.py:7` — `__version__ = "0.6.2"` → `"0.6.3"`
- `...

### Prompt 2

OK, we were waiting on punt labs to be approved by PyPI as an org, but there is a transfer function so we can publish in my personal account and then go from there. So you can switch to work on PyPI publishing for langlearn-types.  However ** you need to prefix it with punt- and you need to migrate langlearn-tts to punt- as well. This is been part of our plan.

### Prompt 3

OK, make sure the beads are correct in both projects.

### Prompt 4

Can we run an experiment? I'd like to register langlearn-tts as an MCP service with our claude code session.

### Prompt 5

project-local this is just a quick test.

### Prompt 6

OK, can you use synthesize to say something to me in English?

### Prompt 7

This is f*cking awesome. We are going to be famous.

### Prompt 8

First, we have a small bug.  The rachel voice is somewhere in our prompts and it is wrong.  I have seen that elsewhere.

### Prompt 9

Not sure how to map those to the ones I see in the dashboard, such as https://elevenlabs.io/app/voice-library?voiceId=1t1EeRixsJrKbiF1zwM6

### Prompt 10

Matilda

### Prompt 11

yes

