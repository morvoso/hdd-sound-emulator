# Credits and Attributions

## Linux Core Application and Monitoring Engine
- **Repository Origin**: [https://github.com/morvoso/hdd-sound-emulator](https://github.com/morvoso/hdd-sound-emulator) (`git@github.com:morvoso/hdd-sound-emulator.git`)
- **Author and Maintainer**: morvoso and project contributors.
- **Architecture and Implementation**:
  - Linux `/proc/diskstats` kernel polling engine (`retro_hdd_clicker.py`).
  - PyQt6 system tray integration, LED status indicator, and Sound Profile Dashboard (`QDialog`).
  - Multi-voice audio pool (`QtMultimedia`) and randomized WAV selection engine.
  - Acoustic seek synthesis scripts (`generate_sounds.py`) and icon generator (`generate_icons.py`).

## Audio Libraries (hdd-sounds/)
- **Original Project and Audio Curation**: The hard disk and floppy drive recordings (`1980s`, `1990s`, `2000s`, `5'25 Floppy Drives`, etc.) in the `hdd-sounds/` directory are curated from **DiskClick by Deervo**.
  - **DiskClick Project Page**: [https://deervo.itch.io/diskclick](https://deervo.itch.io/diskclick)
  - **Author**: Deervo (`deervo.itch.io`) and community archivists.
  - **Usage**: The application scans these folders and randomly plays from the available WAV files (`load.wav`, `load2.wav`, `looping.wav`, `load3.wav`) when SSD activity occurs.

---

## Support Deervo
Deervo recorded and curated these historical computer hardware audio samples.

If you use these hard drive sound sets, consider visiting Deervo's itch.io page to support their work:
**[Donate to DiskClick on itch.io](https://deervo.itch.io/diskclick)**

---

## Licensing Summary
- **Source Code (`*.py`, `*.sh`)**: Licensed under the MIT License (see `LICENSE`).
- **Audio Assets (`hdd-sounds/`)**: Curated by Deervo under Creative Commons Attribution (CC BY 4.0) and community freeware terms.
