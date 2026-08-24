#!/usr/bin/env bash
# Verify TBO 2 starts on the available Qt platform plugins (Wayland/X11/offscreen).
# Usage: bash test_platforms.sh
set -uo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT/src"

PROBE=$(cat << 'PY'
import os
import sys
import tempfile

os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp()

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from tbo.resources import find_asset_root
from tbo.ui.main_window import MainWindow

app = QApplication(sys.argv)
platform = app.platformName()
print("platform:", platform)

window = MainWindow(asset_root=find_asset_root())
QTimer.singleShot(200, app.quit)
app.exec()
window.close()
print("started-and-exited-on:", platform)
PY
)

run_probe() {
    local platform="$1"
    local label="$2"
    echo "--- $label ($platform) ---"
    if QT_QPA_PLATFORM="$platform" timeout 20 python3 -c "$PROBE" 2>/dev/null; then
        echo "  OK: $label"
        return 0
    else
        echo "  SKIP/FAIL: $label"
        return 1
    fi
}

status=0
echo "=== TBO platform probe ==="
echo "DISPLAY=${DISPLAY:-<unset>} WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-<unset>}"

# Always test offscreen (headless) as the baseline.
run_probe offscreen "Offscreen (headless)" || status=1

# X11: requires an X server reachable via DISPLAY.
if [ -n "${DISPLAY:-}" ]; then
    run_probe xcb "X11 (xcb)" || status=1
else
    echo "  (no DISPLAY; skipping X11 test)"
fi

# Wayland: requires a compositor reachable via WAYLAND_DISPLAY.
if [ -n "${WAYLAND_DISPLAY:-}" ]; then
    run_probe wayland "Wayland" || status=1
else
    echo "  (no WAYLAND_DISPLAY; skipping Wayland test)"
fi

echo "=== Done ==="
exit $status
