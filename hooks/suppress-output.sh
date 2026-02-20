#!/usr/bin/env bash
# Suppress verbose MCP tool output in the UI panel.
#
# updatedMCPToolOutput: short summary shown in the tool-result panel.
# additionalContext: full tool response passed to the model as context.

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

RESULT=$(echo "$INPUT" | jq -r '
  def unpack:
    if type == "string" then
      (fromjson? // .)
    else
      .
    end;
  if (.tool_response | type) == "array" then
    (.tool_response[0].text // "" | unpack)
  else
    (.tool_response | unpack)
  end
')

TEXT_COUNT=$(echo "$INPUT" | jq -r '
  if (.tool_input.texts | type) == "array" then
    (.tool_input.texts | length)
  else
    empty
  end
')
PAIR_COUNT=$(echo "$INPUT" | jq -r '
  if (.tool_input.pairs | type) == "array" then
    (.tool_input.pairs | length)
  else
    empty
  end
')

SUMMARY="done"
case "$TOOL" in
  mcp__langlearn-tts__synthesize|mcp__langlearn_tts__synthesize)
    SUMMARY="audio saved"
    ;;
  mcp__langlearn-tts__synthesize_batch|mcp__langlearn_tts__synthesize_batch)
    if [[ -n "$TEXT_COUNT" ]]; then
      SUMMARY="batch saved (${TEXT_COUNT} files)"
    else
      SUMMARY="batch saved"
    fi
    ;;
  mcp__langlearn-tts__synthesize_pair|mcp__langlearn_tts__synthesize_pair)
    SUMMARY="pair saved"
    ;;
  mcp__langlearn-tts__synthesize_pair_batch|mcp__langlearn_tts__synthesize_pair_batch)
    if [[ -n "$PAIR_COUNT" ]]; then
      SUMMARY="pairs saved (${PAIR_COUNT} files)"
    else
      SUMMARY="pairs saved"
    fi
    ;;
  *)
    SUMMARY="done"
    ;;
esac

jq -n --arg s "$SUMMARY" --arg ctx "$RESULT" '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    updatedMCPToolOutput: $s,
    additionalContext: $ctx
  }
}'
