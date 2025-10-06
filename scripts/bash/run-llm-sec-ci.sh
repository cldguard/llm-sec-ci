#!/usr/bin/env bash
set -euo pipefail
TARGET_ROOT="${1:?Usage: run-llm-sec-ci.sh <TARGET_ROOT>}"
echo "Running cross-platform LLM-Sec-CI scan for $TARGET_ROOT"
