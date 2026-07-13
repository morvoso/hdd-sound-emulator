# Retro 90s HDD Sound Emulator for Linux

A background utility and system tray application for Linux that plays mechanical hard drive seek and click sounds whenever your SSD performs read or write operations.

---

## Features

- **Low CPU Usage (/proc/diskstats)**: Reads kernel block device counters from `/proc/diskstats` every 45ms. Does not require external polling loops or elevated system permissions.
- **Sound Libraries (hdd-sounds/)**:
  - Automatically discovers sample folders curated by Deervo's DiskClick (including sounds from models like the Seagate ST-225, Western Digital Caviar 140, Quantum Fireball 540AT, IBM Deskstar 75GXP, and 3.5" or 5.25" floppy drives).
  - Includes 4 synthesized seek sound profiles (Caviar, Fireball, Deskstar, Medalist).
- **Randomized WAV Selection & Ambient Filtering**:
  - When disk activity is detected, the audio engine randomly selects from the active folder's seek/load samples (`load.wav`, `load2.wav`, `load3.wav`).
  - Automatically filters out continuous ambient idle loops (`looping.wav`, `motor.wav`) from the seek click pool to prevent muddy background overlapping.
  - **Random Drive on Every Click mode**: An optional mode that randomly picks both a drive profile and a seek WAV file for each click event.
- **Exclusive / Clean Playback & Click Rate Limiting**:
  - **Exclusive Playback Mode (Default)**: Plays authentic 3-to-6-second seek sequences cleanly to completion without overlapping, echoing, or mid-way stutter restarts.
  - **Configurable Throttling**: Optional cooldown gaps available from the dashboard or tray menu (Exclusive -1ms default, Authentic Mechanical 125ms, High Rate 65ms, Relaxed 250ms, or Uncapped 0ms).
- **Optional Continuous Background Platter Hum (`looping.wav`)**:
  - Toggle **Enable Background Platter Hum** directly from the system tray menu or sound dashboard to play the continuous, quiet motor rotation hum of your selected drive profile in the background (`whirrrrrr`).
  - When switching drive profiles (or when toggling the emulator on/off), the background hum automatically switches to match the active drive model's acoustic loop or shuts down cleanly.
- **System Tray Menu & Dashboard**:
  - **Submenus**: Right-click the system tray icon to select sound profiles sorted by era (1980s, 1990s, 2000s+, Floppy Drives & CD-ROM) and toggle background platter hum.
  - **Sound Dashboard**: Double-click the tray icon to open the settings dialog to filter profiles, preview audio samples, adjust volume, change the polling rate, and set click rate limits.
  - **Activity Indicator**: The system tray icon shows a red LED indicator during disk activity.

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/morvoso/hdd-sound-emulator.git
# Or via SSH:
# git clone git@github.com:morvoso/hdd-sound-emulator.git

cd hdd-sound-emulator
```

### 2. Run the Installer
```bash
./install.sh
```
**What install.sh does:**
- Checks for Python 3 and PyQt6 (`python3-pyqt6`). If not installed globally, it sets up a local Python virtual environment (`venv/`) and installs `PyQt6`.
- Creates a desktop application menu entry (`~/.local/share/applications/retro-hdd-clicker.desktop`).
- Creates a systemd user service (`~/.config/systemd/user/retro-hdd-clicker.service`) for optional login auto-start.

---

## Usage

### Start the Emulator
Launch from your desktop application menu (`Retro 90s HDD Sound Emulator`) or run directly from the terminal:
```bash
./start_hdd_clicker.sh
```

### Stop the Emulator
```bash
./stop_hdd_clicker.sh
```

### Auto-Start on Login (Systemd)
To enable background auto-start on user login:
```bash
systemctl --user enable --now retro-hdd-clicker.service
```
To check service status or disable auto-start:
```bash
systemctl --user status retro-hdd-clicker.service
systemctl --user disable --now retro-hdd-clicker.service
```

---

## Uninstallation

To remove the desktop shortcut, systemd service, and temporary logs:
```bash
./uninstall.sh
```
*This stops running instances and removes files from `~/.local/share/applications` and `~/.config/systemd/user`. To delete the project files, remove the repository directory (`rm -rf hdd-sound-emulator`).*

---

## Credits and Attribution

### Code and Architecture
- **Repository**: [https://github.com/morvoso/hdd-sound-emulator](https://github.com/morvoso/hdd-sound-emulator)
- **Maintainer**: morvoso and project contributors.
- **License**: MIT License (see `LICENSE`).
- All `/proc/diskstats` monitoring logic, PyQt6 system tray interface, multi-voice QtMultimedia audio pooling, randomized WAV selection, synthesized profiles (`sounds/`), and tray icons (`icons/`) were developed for this project.

### Deervo's DiskClick & Audio Samples (hdd-sounds/)
- The hard disk and floppy drive WAV folders inside `hdd-sounds/` (`1980s`, `1990s`, `2000s`, etc.) are curated from **DiskClick** created by **Deervo**.
  - **DiskClick Project Page**: [https://deervo.itch.io/diskclick](https://deervo.itch.io/diskclick)
  - **Usage**: The application scans these folders and plays from the available WAV samples (`load.wav`, `load2.wav`, `looping.wav`, etc.) when disk activity occurs.
  - **License**: Audio assets are incorporated under Creative Commons Attribution (CC BY 4.0) and community freeware terms (see `CREDITS.md`).

---

## Support Deervo

Deervo recorded, edited, and compiled these historical hardware audio samples.

If you find this utility useful, consider supporting Deervo by visiting the DiskClick project page and making a donation:

**[Donate to DiskClick on itch.io](https://deervo.itch.io/diskclick)**

---
