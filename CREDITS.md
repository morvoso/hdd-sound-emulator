# 🏆 Credits & Attributions

## 🐧 Linux Core Application & Monitoring Engine
- **Repository Origin**: [https://github.com/morvoso/hdd-sound-emulator](https://github.com/morvoso/hdd-sound-emulator) (`git@github.com:morvoso/hdd-sound-emulator.git`)
- **Author & Maintainer**: **morvoso** and project contributors.
- **Architecture & Implementation**:
  - Custom, ultra-lightweight Linux `/proc/diskstats` kernel polling engine (`retro_hdd_clicker.py`).
  - PyQt6 system tray integration, visual LED status indicator, and interactive Sound Profile Dashboard (`QDialog`).
  - Multi-voice overlapping audio pool (`QtMultimedia`) and dynamic randomized `.wav` selection engine per click.
  - Custom acoustic seek synthesis scripts (`generate_sounds.py`) and retro icon generator (`generate_icons.py`).

## 💾 Vintage Audio Libraries (`hdd-sounds/`)
- **Original Project & Audio Curation**: The extensive library of vintage hard disk and floppy drive recordings (`1980s`, `1990s`, `2000s`, `5'25 Floppy Drives`, etc.) in the `hdd-sounds/` directory is curated from **DiskClick by Deervo**.
  - **DiskClick Project Page**: [https://deervo.itch.io/diskclick](https://deervo.itch.io/diskclick)
  - **Author / Creator**: **Deervo** (`deervo.itch.io`) & retro community archivists.
  - **How We Used the Sounds**: Every folder from DiskClick is automatically discovered by our Linux engine. Whenever your SSD performs physical read/write operations, our engine randomly selects one of Deervo's curated `.wav` files inside the chosen folder (`load.wav`, `load2.wav`, `looping.wav`, `load3.wav`) to produce dynamic, authentic mechanical chatter without repetition.

---

## ❤️ Support & Donate to Deervo!
Deervo spent immense time and effort gathering, cleaning, and curating these unmistakable sounds of classic computer history from physical 1980s, 1990s, and 2000s hardware.

If you enjoy these nostalgic hard drive clicks on Linux, please consider visiting Deervo's itch.io page and supporting their work by donating:
👉 **[Donate to DiskClick on itch.io ("Name your own price")](https://deervo.itch.io/diskclick)** 👈

---

## 📜 Licensing Summary
- **Source Code (`*.py`, `*.sh`)**: Licensed under the **MIT License** (see `LICENSE`).
- **Audio Assets (`hdd-sounds/`)**: Curated by Deervo and community archivers under **Creative Commons Attribution (CC BY 4.0) / Community Freeware** terms.
