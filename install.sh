#!/usr/bin/env bash
# Retro 90s HDD Sound Emulator - Easiest One-Step Installer
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "  Installing Retro 90s HDD Sound Emulator for Linux  "
echo "=========================================================="
echo ""

# 1. Ensure scripts are executable
chmod +x "$SCRIPT_DIR/retro_hdd_clicker.py" \
         "$SCRIPT_DIR/start_hdd_clicker.sh" \
         "$SCRIPT_DIR/stop_hdd_clicker.sh" \
         "$SCRIPT_DIR/generate_sounds.py" \
         "$SCRIPT_DIR/generate_icons.py" 2>/dev/null || true

# 2. Check for Python 3 & PyQt6
echo "--> Checking Python dependencies..."
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but not found. Please install python3 via your package manager."
    exit 1
fi

if ! python3 -c "import PyQt6.QtCore, PyQt6.QtGui, PyQt6.QtWidgets, PyQt6.QtMultimedia" &>/dev/null; then
    echo "Notice: PyQt6 or QtMultimedia not found in global Python environment."
    echo "--> Attempting to check for package manager or create virtual environment..."
    
    if command -v apt-get &>/dev/null; then
        echo "Hint: On Ubuntu/Debian/Mint, you can run: sudo apt install python3-pyqt6 python3-pyqt6.qtmultimedia"
    elif command -v dnf &>/dev/null; then
        echo "Hint: On Fedora, you can run: sudo dnf install python3-pyqt6"
    elif command -v pacman &>/dev/null; then
        echo "Hint: On Arch Linux, you can run: sudo pacman -S python-pyqt6"
    fi
    
    # Create local venv if global pyqt6 isn't present
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        echo "--> Creating local Python virtual environment ($SCRIPT_DIR/venv)..."
        python3 -m venv "$SCRIPT_DIR/venv"
        "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip
        "$SCRIPT_DIR/venv/bin/pip" install PyQt6
    fi
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python3"
else
    echo "Global PyQt6 installation detected."
    PYTHON_CMD="python3"
fi

# 3. Create Desktop Application Menu Entry (~/.local/share/applications/)
echo "--> Creating Desktop Application Launcher..."
APP_DIR="$HOME/.local/share/applications"
mkdir -p "$APP_DIR"
DESKTOP_FILE="$APP_DIR/retro-hdd-clicker.desktop"

cat << EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=Retro 90s HDD Sound Emulator
Comment=Simulate authentic 1980s, 1990s, and 2000s mechanical hard drive seek/click noises on SSD activity
Exec="$SCRIPT_DIR/start_hdd_clicker.sh"
Icon=$SCRIPT_DIR/icons/icon_active.png
Terminal=false
Type=Application
Categories=Utility;System;Monitor;
Keywords=hdd;ssd;clicker;retro;sound;disk;activity;
EOF

chmod +x "$DESKTOP_FILE"
echo "Desktop shortcut created at $DESKTOP_FILE"

# 4. Optional Systemd Background Auto-Start Service
echo "--> Setting up systemd user service..."
SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"
SERVICE_FILE="$SYSTEMD_DIR/retro-hdd-clicker.service"

# Use either global python3 or venv python3 in systemd service
cat << EOF > "$SERVICE_FILE"
[Unit]
Description=Retro 90s HDD Sound Emulator (Simulated Mechanical SSD Activity Sound & Tray)
After=graphical-session.target sound.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStart=$PYTHON_CMD "$SCRIPT_DIR/retro_hdd_clicker.py"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload || true
echo "Systemd service installed ($SERVICE_FILE)"

echo ""
echo "=========================================================="
echo "  Installation Complete!"
echo "=========================================================="
echo ""
echo "To START the emulator right now:"
echo "    $SCRIPT_DIR/start_hdd_clicker.sh"
echo ""
echo "To auto-start on system login (Systemd):"
echo "    systemctl --user enable --now retro-hdd-clicker.service"
echo ""
echo "To STOP or UNINSTALL:"
echo "    $SCRIPT_DIR/uninstall.sh"
echo "=========================================================="
