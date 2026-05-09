# Bug: Default voice "rachel" not available in ElevenLabs

**Tool:** langlearn-tts MCP server
**Provider:** ElevenLabs

## Problem

All four synthesis functions (`synthesize`, `synthesize_batch`, `synthesize_pair`, `synthesize_pair_batch`) fail when called without an explicit `voice` parameter. The server defaults to `"rachel"`, which is not in the available voice list.

**Error message:**

```text
Error executing tool synthesize: Unknown voice 'rachel'. Available: adam, alice, bella, bill, brian, callum, charlie, chris, daniel, eric ... (22 total)
```


## Expected Behavior

Calls without a `voice` parameter should succeed using a valid default voice.

## Suggested Fix

Update the default voice constant to a voice that exists in the current ElevenLabs account (e.g., `"alice"` or `"daniel"`). Alternatively, add `"rachel"` to the ElevenLabs voice library if it was removed unintentionally.

## Workaround

Specify `voice` explicitly on every call. For pair functions, specify both `voice1` and `voice2`.
