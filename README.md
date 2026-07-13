# Retro 90s HDD Sound Emulator for Linux

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux%20%2F%20PyQt6-green.svg)]()

A lightweight, ultra-responsive background service and system tray application for Linux that simulates authentic 1980s, 1990s, and 2000s mechanical hard drive seek and click noises whenever your SSD (nvme0n1, nvme1n1, sda, etc.) performs read or write operations.

---

## Key Features

- **Zero Overhead & Ultra-Lightweight (/proc/diskstats)**: Reads kernel block device counters directly from memory (`/proc/diskstats`) every 45ms (taking < 0.02ms). Uses practically 0.00% idle CPU without spawning external polling loops.
- **68+ Authentic HDD & Floppy Sound Libraries (hdd-sounds/)**:
  - Automatically discovers over 64 classic hardware sample folders curated by Deervo's DiskClick (including the 1987 Seagate ST-225, 1990 WD Caviar 140, 1996 Quantum Fireball 540AT, 2001 IBM Deskstar 75GXP, plus 3.5" and 5.25" Floppy Drives).
  - Includes 4 custom synthesized acoustic profiles (Caviar, Fireball, Deskstar, Medalist).
- **Dynamic Randomized WAV Selection per Click**:
  - Whenever disk activity is detected, the audio engine randomly chooses one of the WAV files inside the selected sound folder (`load.wav`, `load2.wav`, `looping.wav`, `load3.wav`). This creates organic, non-repetitive mechanical chatter.
  - **Random Drive on Every Click mode**: Enable this option for total retro computing chaos where every single click picks both a random vintage drive and a random WAV file.
- **Categorized System Tray Menu & Dashboard**:
  - **Categorized Submenus**: Right-click the system tray icon to browse clean, organized submenus (1980s Hard Drives, 1990s Hard Drives, 2000s+ Hard Drives, Floppy Drives & CD-ROM).
  - **Interactive Sound Dashboard**: Double-click the tray icon to open our Qt6 dashboard where you can filter profiles by era, preview any drive instantly, and adjust volume or sensitivity.
  - **Visual HDD Activity Light**: The system tray icon pulses a retro RED activity LED (`icon_active.png`) right on your desktop panel in real-time with disk activity.

---

## Installation

We provide an automated installer script that works across all major Linux distributions (Ubuntu, Debian, Fedora, Arch, Linux Mint, etc.).

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
**What install.sh does automatically:**
- Checks for Python 3 and PyQt6 (`python3-pyqt6`). If not found globally, it automatically sets up a clean local Python virtual environment (`venv/`) and installs `PyQt6`.
- Creates a Desktop Application Shortcut (`~/.local/share/applications/retro-hdd-clicker.desktop`) so you can launch the emulator directly from your application menu (GNOME, KDE, XFCE, Cinnamon).
- Installs an optional Systemd User Service (`~/.config/systemd/user/retro-hdd-clicker.service`) so you can easily enable auto-start on login.

---

## How to Start, Stop & Manage

### Start the Emulator
You can launch it from your desktop application menu (`Retro 90s HDD Sound Emulator`), or directly via terminal:
```bash
./start_hdd_clicker.sh
```
*The vintage hard drive icon will appear in your system tray right away. Double-click it to open the Sound Dashboard.*

### Stop the Emulator
```bash
./stop_hdd_clicker.sh
```

### Auto-Start on System Login (Systemd)
To enable the emulator to automatically run in the background whenever you log into your Linux desktop:
```bash
systemctl --user enable --now retro-hdd-clicker.service
```
To check status or disable auto-start:
```bash
systemctl --user status retro-hdd-clicker.service
systemctl --user disable --now retro-hdd-clicker.service
```

---

## How to Uninstall

If you ever wish to remove the system tray shortcuts, background services, and clean up temporary logs, simply run the uninstaller from the project directory:
```bash
./uninstall.sh
```
*This cleanly stops any running instances and removes your desktop and systemd shortcuts (`~/.local/share/applications` and `~/.config/systemd/user`). Your repository files remain untouched unless you choose to delete the directory manually (`rm -rf hdd-sound-emulator`).*

---

## Credits, Origin & Audio Attribution

### Linux Code & Architecture
- **Repository**: [https://github.com/morvoso/hdd-sound-emulator](https://github.com/morvoso/hdd-sound-emulator)
- **Maintainer**: morvoso and project contributors.
- **Code License**: Licensed under the MIT License (see `LICENSE`).
- All Linux kernel `/proc/diskstats` monitoring logic, PyQt6 system tray dashboard, multi-voice QtMultimedia audio pooling, randomized WAV selection engine, synthesized profiles (`sounds/`), and tray icons (`icons/`) were developed originally for this Linux project.

### Deervo's DiskClick & Audio Samples (hdd-sounds/)
- The library of vintage hard disk and floppy drive WAV sample folders inside `hdd-sounds/` (`1980s`, `1990s`, `2000s`, etc.) is curated from **DiskClick** created by **Deervo**.
  - **DiskClick Project Page**: [https://deervo.itch.io/diskclick](https://deervo.itch.io/diskclick)
  - **How We Used His Sounds**: Our application dynamically scans Deervo's sample folders and randomly picks between `load.wav`, `load2.wav`, `looping.wav`, etc., whenever disk activity happens on Linux.
  - **License**: Curated audio assets are incorporated under Creative Commons Attribution (CC BY 4.0) / Community Freeware terms (see `CREDITS.md`).

---

## Support & Donate to Deervo

Deervo spent countless hours recording, cleaning, and archiving these unmistakable, nostalgic sounds from physical 1980s, 1990s, and 2000s computer hardware for the community.

If you enjoy hearing these classic mechanical clicks on your Linux machine, please consider visiting Deervo's itch.io page and showing your appreciation with a donation:

**[Donate to DiskClick on itch.io ("Name your own price")](https://deervo.itch.io/diskclick)**

---
