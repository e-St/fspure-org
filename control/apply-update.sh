#!/usr/bin/env bash
# Apply latest e-St/bellen control files into ROOT (default: cwd).
# Keeps containerEnv.REPOS / PLATFORM. Set BELLEN to a bellen checkout.
ROOT="${ROOT:-.}"
if [ -z "$BELLEN" ] || [ ! -f "$BELLEN/image/VERSION" ]; then
  echo "Set BELLEN to an e-St/bellen checkout." >&2
  exit 1
fi
export ROOT BELLEN GITHUB_REPOSITORY
python3 "$BELLEN/control/render.py"
