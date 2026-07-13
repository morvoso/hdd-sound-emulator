#!/usr/bin/env bash
# Retro 90s HDD Sound Emulator - Uninstaller
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "  Uninstalling Retro 90s HDD Sound Emulator for Linux "
echo "=========================================================="
echo ""

# 1. Stop any currently running instance
echo "--> Stopping running emulator instances..."
if [ -f "$SCRIPT_DIR/stop_hdd_clicker.sh" ]; then
    "$SCRIPT_DIR/stop_hdd_clicker.sh" 2>/dev/null || true
fi
pids=$(pgrep -f "python3.*retro_hdd_clicker.py" || true)
if [ -n "$pids" ]; then
    kill $pids 2>/dev/null || true
fi

# 2. Disable and remove systemd user service if installed
echo "--> Removing systemd user service..."
if command -v systemctl &>/dev/null; then
    systemctl --user disable --now retro-hdd-clicker.service 2>/dev/null || true
    systemctl --user daemon-reload 2>/dev/null || true
fi
rm -f "$HOME/.config/systemd/user/retro-hdd-clicker.service"

# 3. Remove Desktop Application shortcut
echo "--> Removing desktop launcher..."
rm -f "$HOME/.local/share/applications/retro-hdd-clicker.desktop"

# 4. Clean up temporary log files or pid files
rm -f /tmp/retro_hdd_clicker.log "$SCRIPT_DIR/retro_hdd_clicker.pid"

echo ""
echo "=========================================================="
echo " Uninstallation Complete. All system entries removed."
echo " Note: The repository files in $SCRIPT_DIR remain intact."
echo " To completely delete the repository, you can run:"
echo "    rm -rf \"$SCRIPT_DIR\""
echo "=========================================================="
