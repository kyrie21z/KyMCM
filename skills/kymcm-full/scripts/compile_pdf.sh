#!/usr/bin/env bash
# Compatibility wrapper. Core workspace and compilation logic lives in Python.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python "$SCRIPT_DIR/compile_pdf.py" "$@"
