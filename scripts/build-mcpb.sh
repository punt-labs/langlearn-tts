#!/usr/bin/env bash
# Build the .mcpb Desktop Extension bundle.
#
# Prerequisites: npm install -g @anthropic-ai/mcpb
#
# Usage: ./scripts/build-mcpb.sh
#
# Output: dist/punt-langlearn-tts-<version>.mcpb

set -euo pipefail

cd "$(dirname "$0")/.."

# Extract version from manifest.json.
version=$(python3 -c "import json; print(json.load(open('manifest.json'))['version'])")

# Verify manifest version matches __init__.py version.
init_version=$(python3 -c "
import re
text = open('src/langlearn_tts/__init__.py').read()
m = re.search(r'__version__\s*=\s*\"(.+?)\"', text)
print(m.group(1) if m else '')
")

if [ -z "$init_version" ]; then
    echo "ERROR: Could not find __version__ in src/langlearn_tts/__init__.py" >&2
    exit 1
fi

if [ "$version" != "$init_version" ]; then
    echo "ERROR: Version mismatch — manifest.json ($version) != __init__.py ($init_version)" >&2
    exit 1
fi

echo "Building punt-langlearn-tts $version .mcpb bundle..."

mkdir -p dist
mcpb pack . "dist/punt-langlearn-tts-${version}.mcpb"

# Create stable-named copy for GitHub release (latest/download/punt-langlearn-tts.mcpb).
cp "dist/punt-langlearn-tts-${version}.mcpb" "dist/punt-langlearn-tts.mcpb"

echo "Built: dist/punt-langlearn-tts-${version}.mcpb"
echo "       dist/punt-langlearn-tts.mcpb (stable name)"
echo "Size: $(du -h "dist/punt-langlearn-tts-${version}.mcpb" | cut -f1)"
