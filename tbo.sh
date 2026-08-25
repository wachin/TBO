#!/usr/bin/env bash

set -euo pipefail

TBO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TBO_PYTHON="${TBO_PYTHON:-python3}"

if ! command -v "$TBO_PYTHON" >/dev/null 2>&1; then
    printf 'TBO: Python interpreter not found: %s\n' "$TBO_PYTHON" >&2
    printf 'Install Python 3.11 or later, or set TBO_PYTHON.\n' >&2
    exit 127
fi

if ! "$TBO_PYTHON" -c 'import PyQt6' >/dev/null 2>&1; then
    printf 'TBO: PyQt6 is not installed for %s.\n' "$TBO_PYTHON" >&2
    printf "Install it with: %s -m pip install -e '%s/tbo_next'\n" \
        "$TBO_PYTHON" "$TBO_ROOT" >&2
    exit 1
fi

export PYTHONPATH="$TBO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

exec "$TBO_PYTHON" -m tbo "$@"
