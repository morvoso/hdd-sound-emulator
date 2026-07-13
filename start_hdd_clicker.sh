#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/retro_hdd_clicker.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "Retro 90s HDD Sound Emulator is already running (PID: $(cat "$PID_FILE"))."
    echo "To stop it, run: $SCRIPT_DIR/stop_hdd_clicker.sh"
    exit 0
fi

if [ -x "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python3"
else
    PYTHON_CMD="python3"
fi

echo "Starting Retro 90s HDD Sound Emulator in the background..."
nohup "$PYTHON_CMD" "$SCRIPT_DIR/retro_hdd_clicker.py" > /tmp/retro_hdd_clicker.log 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
echo "Started successfully with PID $PID!"
echo "System tray icon is now active. Right-click or double-click the icon to configure sound profiles or disable/enable."
