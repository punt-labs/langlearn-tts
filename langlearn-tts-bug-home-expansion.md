# Bug: ${HOME} not expanded in default output_dir

**Tool:** langlearn-tts MCP server

## Problem

When `output_dir` is not explicitly provided, the server uses a default path containing the literal string `${HOME}` instead of expanding it to the actual home directory. Files are written to a directory literally named `${HOME}/langlearn-audio/` rather than `/Users/<username>/langlearn-audio/`.

**Returned path (broken):**
```
${HOME}/langlearn-audio/daniel_Guten_Tag,_wie_geht_.mp3
```

**Expected path:**
```
/Users/jfreeman/langlearn-audio/daniel_Guten_Tag,_wie_geht_.mp3
```

**Workaround confirmed:** Passing an absolute path via `output_dir` works correctly.

## Suggested Fix

Wherever the default `output_dir` is set, apply shell/environment variable expansion. In Python:

```python
# Option A
import os
output_dir = os.path.expandvars(output_dir)

# Option B
from pathlib import Path
output_dir = Path.home() / "langlearn-audio"
```

Also expand `~` if used:

```python
output_dir = os.path.expanduser(output_dir)
```
