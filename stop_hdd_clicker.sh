#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/retro_hdd_clicker.pid"

if [ -f "$PID_FILE" ]; then
    PID="$(cat "$PID_FILE")"
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping Retro 90s HDD Sound Emulator (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "Stopped."
        exit 0
    else
        echo "Process $PID not running. Cleaning up PID file."
        rm -f "$PID_FILE"
    fi
fi

# Fallback kill by name if running without pidfile
pids=$(pgrep -f "python3.*retro_hdd_clicker.py")
if [ -n "$pids" ]; then
    echo "Killing remaining retro_hdd_clicker processes: $pids"
    kill $pids
    echo "Stopped."
else
    echo "Retro 90s HDD Sound Emulator is not currently running."
fi
