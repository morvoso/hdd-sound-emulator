#!/usr/bin/env python3
import sys
import os
import time
import random
import subprocess
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction, QActionGroup
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QGroupBox, QCheckBox, QRadioButton,
    QButtonGroup, QPushButton, QProgressBar, QWidget, QComboBox,
    QListWidget, QListWidgetItem, QSlider, QSplitter
)
from PyQt6.QtMultimedia import QSoundEffect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
HDD_SOUNDS_DIR = os.path.join(BASE_DIR, "hdd-sounds")
ICONS_DIR = os.path.join(BASE_DIR, "icons")

class BlockDeviceMonitor(QObject):
    activity_detected = pyqtSignal(str, int) # sound_type ("single", "double", "crunch" or "any"), delta_magnitude

    def __init__(self, monitored_drives, poll_interval_ms=45):
        super().__init__()
        self.monitored_drives = set(monitored_drives)
        self.poll_interval_ms = poll_interval_ms
        self.last_stats = {}
        self.enabled = True
        self.total_clicks = 0
        self.total_sectors_read = 0
        self.total_sectors_written = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_activity)
        self._read_stats()

    def start_monitoring(self):
        self.timer.start(self.poll_interval_ms)

    def set_interval(self, ms):
        self.poll_interval_ms = ms
        if self.timer.isActive():
            self.timer.setInterval(ms)

    def _read_stats(self):
        stats = {}
        try:
            with open("/proc/diskstats", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 14:
                        dev_name = parts[2]
                        if dev_name in self.monitored_drives:
                            reads_completed = int(parts[3])
                            sectors_read = int(parts[5])
                            writes_completed = int(parts[7])
                            sectors_written = int(parts[9])
                            stats[dev_name] = (reads_completed, sectors_read, writes_completed, sectors_written)
        except Exception as e:
            pass
        return stats

    def check_activity(self):
        if not self.enabled:
            return
            
        current_stats = self._read_stats()
        delta_ops = 0
        delta_sectors = 0
        
        for dev, cur in current_stats.items():
            if dev in self.last_stats:
                old = self.last_stats[dev]
                reads_diff = max(0, cur[0] - old[0])
                sec_r_diff = max(0, cur[1] - old[1])
                writes_diff = max(0, cur[2] - old[2])
                sec_w_diff = max(0, cur[3] - old[3])
                
                delta_ops += (reads_diff + writes_diff)
                delta_sectors += (sec_r_diff + sec_w_diff)
                
                self.total_sectors_read += sec_r_diff
                self.total_sectors_written += sec_w_diff

        self.last_stats = current_stats
        
        if delta_ops > 0 or delta_sectors > 0:
            self.total_clicks += 1
            intensity = delta_ops + (delta_sectors / 16.0)
            if intensity <= 2:
                sound_type = "single"
            elif intensity <= 10:
                sound_type = "double"
            else:
                sound_type = "crunch"
            self.activity_detected.emit(sound_type, int(intensity))


class AudioController:
    def __init__(self, profiles_dict, initial_profile="caviar", volume=0.8, engine="qt"):
        self.profiles = profiles_dict # key -> {name, path, category, wavs}
        self.profile = initial_profile
        self.volume = volume
        self.engine = engine # "qt" or "paplay"
        self.loaded_pools = {} # wav_path -> list of QSoundEffect instances
        self.current_wav_list = [] # list of wav file paths for current profile
        self.load_profile(initial_profile)

    def load_profile(self, profile_key):
        self.profile = profile_key
        self.loaded_pools.clear()
        self.current_wav_list.clear()
        
        if profile_key == "random_drive" or profile_key not in self.profiles:
            return
            
        wav_files = self.profiles[profile_key]["wavs"]
        self.current_wav_list = wav_files
        
        # Preload QSoundEffect pools for quick playback
        for wav_path in wav_files:
            pool = []
            for _ in range(2): # 2 instances per wav file to allow overlapping
                fx = QSoundEffect()
                fx.setSource(QUrl.fromLocalFile(wav_path))
                fx.setVolume(self.volume)
                pool.append(fx)
            self.loaded_pools[wav_path] = pool

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        for wav_path, pool in self.loaded_pools.items():
            for fx in pool:
                fx.setVolume(self.volume)

    def play(self, sound_type="any"):
        target_wav = None
        
        if self.profile == "random_drive":
            # Pick a random profile from all discovered profiles
            all_keys = [k for k in self.profiles.keys() if self.profiles[k]["wavs"]]
            if not all_keys:
                return
            rand_key = random.choice(all_keys)
            wavs = self.profiles[rand_key]["wavs"]
            if not wavs:
                return
            target_wav = random.choice(wavs)
        else:
            if not self.current_wav_list:
                return
            
            # If the profile specifically has "single.wav", "double.wav", "crunch.wav" matching intensity, try using that
            if sound_type in ["single", "double", "crunch"]:
                matching = [w for w in self.current_wav_list if os.path.splitext(os.path.basename(w))[0].lower() == sound_type]
                if matching:
                    target_wav = matching[0]
            
            # Otherwise, randomly select one of the WAV files inside this profile's folder!
            if not target_wav:
                target_wav = random.choice(self.current_wav_list)

        if not target_wav:
            return

        if self.engine == "paplay":
            try:
                subprocess.Popen(["paplay", target_wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        else:
            # QtMultimedia playback
            pool = self.loaded_pools.get(target_wav)
            if not pool:
                # If playing on the fly (e.g. random_drive mode or dynamic selection)
                fx = QSoundEffect()
                fx.setSource(QUrl.fromLocalFile(target_wav))
                fx.setVolume(self.volume)
                fx.play()
                # Store temporarily so it doesn't get garbage collected instantly
                self.loaded_pools[target_wav] = [fx]
                return

            played = False
            for fx in pool:
                if not fx.isPlaying():
                    fx.setVolume(self.volume)
                    fx.play()
                    played = True
                    break
            if not played and pool:
                pool[0].setVolume(self.volume)
                pool[0].play()


class SettingsDialog(QDialog):
    def __init__(self, monitor, audio_ctrl, profiles_dict, on_profile_changed_cb, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self.audio_ctrl = audio_ctrl
        self.profiles = profiles_dict
        self.on_profile_changed_cb = on_profile_changed_cb
        self.setWindowTitle("Retro 90s HDD Clicker - Sound Selector & Dashboard")
        self.setMinimumSize(580, 520)
        self.setup_ui()
        
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(500)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_lbl = QLabel("<b>Retro 90s HDD Clicker Dashboard</b><br>Monitor live disk activity and choose from 60+ authentic vintage drive sounds.")
        header_lbl.setStyleSheet("font-size: 13px; color: #222; margin-bottom: 6px;")
        main_layout.addWidget(header_lbl)
        
        # Live Stats Box
        stats_box = QGroupBox("Live SSD Activity Metrics")
        stats_layout = QHBoxLayout(stats_box)
        self.lbl_clicks = QLabel("Total Clicks: 0")
        self.lbl_read = QLabel("Sectors Read: 0 (0.0 MB)")
        self.lbl_written = QLabel("Sectors Written: 0 (0.0 MB)")
        stats_layout.addWidget(self.lbl_clicks)
        stats_layout.addWidget(self.lbl_read)
        stats_layout.addWidget(self.lbl_written)
        main_layout.addWidget(stats_box)
        
        # Sound Library Browser Group
        sound_box = QGroupBox("Sound Library & Profile Selector")
        sound_layout = QVBoxLayout(sound_box)
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter Category:"))
        self.combo_category = QComboBox()
        self.combo_category.addItems([
            "All Categories & Eras",
            "⚡ Built-in Synthesized Profiles",
            "💾 1980s Hard Drives",
            "💾 1990s Hard Drives",
            "💾 2000s+ Hard Drives",
            "💾 Floppy Drives & CD-ROM",
            "💾 Other Classic & Custom Drives"
        ])
        self.combo_category.currentIndexChanged.connect(self.populate_list)
        filter_layout.addWidget(self.combo_category, 1)
        sound_layout.addLayout(filter_layout)
        
        # Profile List Widget
        self.list_profiles = QListWidget()
        self.list_profiles.itemSelectionChanged.connect(self.on_selection_changed)
        self.list_profiles.itemDoubleClicked.connect(self.on_item_double_clicked)
        sound_layout.addWidget(self.list_profiles, 1)
        
        # Buttons under profile list
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton("🎧 Preview Random Sound from Folder")
        self.btn_preview.clicked.connect(self.preview_selected_profile)
        self.btn_preview.setEnabled(False)
        
        self.btn_apply = QPushButton("✔ Apply Selected Profile")
        self.btn_apply.setStyleSheet("font-weight: bold; padding: 5px;")
        self.btn_apply.clicked.connect(self.apply_selected_profile)
        self.btn_apply.setEnabled(False)
        
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_apply)
        sound_layout.addLayout(btn_layout)
        
        main_layout.addWidget(sound_box, 1)
        
        # Volume & Backend Box
        ctrl_box = QGroupBox("Audio Settings & Engine")
        ctrl_layout = QHBoxLayout(ctrl_box)
        
        ctrl_layout.addWidget(QLabel("Volume:"))
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(int(self.audio_ctrl.volume * 100))
        self.slider_vol.valueChanged.connect(self.on_volume_changed)
        ctrl_layout.addWidget(self.slider_vol, 1)
        self.lbl_vol_val = QLabel(f"{int(self.audio_ctrl.volume * 100)}%")
        ctrl_layout.addWidget(self.lbl_vol_val)
        
        ctrl_layout.addSpacing(15)
        ctrl_layout.addWidget(QLabel("Backend:"))
        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["PyQt6 QtMultimedia (Multi-Voice)", "PulseAudio / PipeWire (paplay)"])
        self.combo_engine.setCurrentIndex(0 if self.audio_ctrl.engine == "qt" else 1)
        self.combo_engine.currentIndexChanged.connect(self.on_engine_changed)
        ctrl_layout.addWidget(self.combo_engine)
        
        main_layout.addWidget(ctrl_box)
        
        # Close Button
        btn_close = QPushButton("Close Dashboard")
        btn_close.clicked.connect(self.accept)
        main_layout.addWidget(btn_close)
        
        self.populate_list()

    def populate_list(self):
        self.list_profiles.clear()
        filter_idx = self.combo_category.currentIndex()
        cat_map = {
            1: "built_in",
            2: "1980s",
            3: "1990s",
            4: "2000s",
            5: "floppy",
            6: "classic"
        }
        target_cat = cat_map.get(filter_idx)
        
        # Add Special Random option first if viewing all
        if filter_idx == 0:
            item_rand = QListWidgetItem("🎲 [ Special ] Random Drive / Folder on Every Click")
            item_rand.setData(Qt.ItemDataRole.UserRole, "random_drive")
            if self.audio_ctrl.profile == "random_drive":
                item_rand.setFont(self._bold_font())
            self.list_profiles.addItem(item_rand)
            
        for key, data in sorted(self.profiles.items(), key=lambda x: x[1]["name"]):
            if target_cat and data["category"] != target_cat:
                continue
            num_wavs = len(data["wavs"])
            display_text = f"{data['name']}  ({num_wavs} WAV files)"
            if key == self.audio_ctrl.profile:
                display_text = "★ " + display_text + "  [ ACTIVE ]"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, key)
            if key == self.audio_ctrl.profile:
                item.setFont(self._bold_font())
            self.list_profiles.addItem(item)

    def _bold_font(self):
        f = self.font()
        f.setBold(True)
        return f

    def on_selection_changed(self):
        items = self.list_profiles.selectedItems()
        if items:
            self.btn_preview.setEnabled(True)
            self.btn_apply.setEnabled(True)
        else:
            self.btn_preview.setEnabled(False)
            self.btn_apply.setEnabled(False)

    def preview_selected_profile(self):
        items = self.list_profiles.selectedItems()
        if not items:
            return
        key = items[0].data(Qt.ItemDataRole.UserRole)
        if key == "random_drive":
            self.audio_ctrl.play()
            return
            
        data = self.profiles.get(key)
        if not data or not data["wavs"]:
            return
        # Randomly select one of the WAV files in this folder to audition
        sample_wav = random.choice(data["wavs"])
        try:
            subprocess.Popen(["paplay", sample_wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            fx = QSoundEffect()
            fx.setSource(QUrl.fromLocalFile(sample_wav))
            fx.setVolume(self.audio_ctrl.volume)
            fx.play()

    def apply_selected_profile(self):
        items = self.list_profiles.selectedItems()
        if not items:
            return
        key = items[0].data(Qt.ItemDataRole.UserRole)
        self.audio_ctrl.load_profile(key)
        if self.on_profile_changed_cb:
            self.on_profile_changed_cb(key)
        self.populate_list()

    def on_item_double_clicked(self, item):
        self.apply_selected_profile()
        self.preview_selected_profile()

    def on_volume_changed(self, val):
        self.lbl_vol_val.setText(f"{val}%")
        self.audio_ctrl.set_volume(val / 100.0)

    def on_engine_changed(self, idx):
        self.audio_ctrl.engine = "qt" if idx == 0 else "paplay"

    def update_stats(self):
        self.lbl_clicks.setText(f"Total Clicks Triggered: {self.monitor.total_clicks:,}")
        mb_read = (self.monitor.total_sectors_read * 512) / (1024 * 1024)
        mb_written = (self.monitor.total_sectors_written * 512) / (1024 * 1024)
        self.lbl_read.setText(f"Sectors Read: {self.monitor.total_sectors_read:,} ({mb_read:.2f} MB)")
        self.lbl_written.setText(f"Sectors Written: {self.monitor.total_sectors_written:,} ({mb_written:.2f} MB)")


class RetroHDDClickerApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.setQuitOnLastWindowClosed(False)
        
        # Discover all sound profiles across sounds/ and hdd-sounds/
        self.profiles = self.discover_all_profiles()
        
        # Discover block devices
        self.available_drives = self.discover_drives()
        monitored = [d for d in self.available_drives if not d.startswith(("loop", "ram", "zram"))]
        if not monitored:
            monitored = self.available_drives
            
        self.monitor = BlockDeviceMonitor(monitored, poll_interval_ms=45)
        
        # Default to Western Digital Caviar if available, or first profile
        initial_prof = "built_in:caviar" if "built_in:caviar" in self.profiles else list(self.profiles.keys())[0]
        self.audio_ctrl = AudioController(self.profiles, initial_profile=initial_prof, volume=0.8, engine="qt")
        
        # Load tray icons
        self.icon_idle = QIcon(os.path.join(ICONS_DIR, "icon_idle.png"))
        self.icon_active = QIcon(os.path.join(ICONS_DIR, "icon_active.png"))
        self.icon_disabled = QIcon(os.path.join(ICONS_DIR, "icon_disabled.png"))
        
        # Setup System Tray
        self.tray_icon = QSystemTrayIcon(self.icon_idle, self)
        self.tray_icon.setToolTip("Retro 90s HDD Clicker (Active)")
        
        self.setup_menu()
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        
        self.monitor.activity_detected.connect(self.on_activity)
        self.icon_reset_timer = QTimer(self)
        self.icon_reset_timer.setSingleShot(True)
        self.icon_reset_timer.timeout.connect(self.reset_tray_icon)
        
        self.monitor.start_monitoring()
        self.settings_dlg = None

    def discover_all_profiles(self):
        profiles = {}
        
        # 1. Built-in synthesized sounds in /sounds
        if os.path.exists(SOUNDS_DIR):
            for item in sorted(os.listdir(SOUNDS_DIR)):
                p_dir = os.path.join(SOUNDS_DIR, item)
                if os.path.isdir(p_dir):
                    wavs = [os.path.join(p_dir, f) for f in sorted(os.listdir(p_dir)) if f.lower().endswith(".wav")]
                    if wavs:
                        names_map = {
                            "caviar": "Western Digital Caviar (1995)",
                            "fireball": "Quantum Fireball (1998)",
                            "deskstar": "IBM Deskstar 75GXP (2000)",
                            "medalist": "Seagate Medalist (1993)"
                        }
                        display = names_map.get(item.lower(), f"Synthesized: {item.capitalize()}")
                        profiles[f"built_in:{item}"] = {
                            "name": f"⚡ {display}",
                            "path": p_dir,
                            "category": "built_in",
                            "wavs": wavs
                        }
                        
        # 2. External hdd-sounds folder
        if os.path.exists(HDD_SOUNDS_DIR):
            for item in sorted(os.listdir(HDD_SOUNDS_DIR)):
                p_dir = os.path.join(HDD_SOUNDS_DIR, item)
                if os.path.isdir(p_dir):
                    wavs = [os.path.join(p_dir, f) for f in sorted(os.listdir(p_dir)) if f.lower().endswith(".wav")]
                    if wavs:
                        # Determine category
                        if item.startswith("198") or item.lower().startswith("random 80"):
                            cat = "1980s"
                            cat_icon = "💾"
                        elif item.startswith("199"):
                            cat = "1990s"
                            cat_icon = "💾"
                        elif item.startswith(("200", "201", "202")):
                            cat = "2000s"
                            cat_icon = "💾"
                        elif "floppy" in item.lower() or "cd-rom" in item.lower():
                            cat = "floppy"
                            cat_icon = "🖨️"
                        else:
                            cat = "classic"
                            cat_icon = "💽"
                            
                        profiles[f"hdd:{item}"] = {
                            "name": f"{cat_icon} {item}",
                            "path": p_dir,
                            "category": cat,
                            "wavs": wavs
                        }
        return profiles

    def discover_drives(self):
        drives = []
        if os.path.exists("/sys/block"):
            for dev in sorted(os.listdir("/sys/block")):
                if dev.startswith(("loop", "ram", "sr")):
                    continue
                drives.append(dev)
        return drives

    def setup_menu(self):
        self.menu = QMenu()
        
        # Enable/Disable toggle
        self.act_enable = QAction("Enable HDD Click Sound", self.menu, checkable=True)
        self.act_enable.setChecked(True)
        self.act_enable.triggered.connect(self.toggle_enable)
        self.menu.addAction(self.act_enable)
        self.menu.addSeparator()
        
        # Sound Profiles Categorized Menu
        self.profile_menu = self.menu.addMenu("Sound Profiles & Libraries")
        
        # Open Dashboard action at top of profile menu
        act_open_sel = QAction("🔍 Open Sound Profile Selector & Dashboard...", self.profile_menu)
        act_open_sel.triggered.connect(self.show_settings)
        self.profile_menu.addAction(act_open_sel)
        self.profile_menu.addSeparator()
        
        self.profile_group = QActionGroup(self)
        
        # Random option
        act_rand = QAction("🎲 Random Drive / Folder on Every Click", self.profile_menu, checkable=True)
        act_rand.setChecked(self.audio_ctrl.profile == "random_drive")
        act_rand.triggered.connect(lambda: self.on_profile_selected("random_drive"))
        self.profile_group.addAction(act_rand)
        self.profile_menu.addAction(act_rand)
        self.profile_menu.addSeparator()
        
        # Submenus for categories
        cats = [
            ("built_in", "⚡ Built-in Synthesized Profiles"),
            ("1980s", "💾 1980s Hard Drives"),
            ("1990s", "💾 1990s Hard Drives"),
            ("2000s", "💾 2000s+ Hard Drives"),
            ("floppy", "🖨️ Floppy Drives & CD-ROM"),
            ("classic", "💽 Other Classic & Custom Drives")
        ]
        
        self.profile_actions = {}
        for cat_key, cat_name in cats:
            matching = [k for k in self.profiles if self.profiles[k]["category"] == cat_key]
            if not matching:
                continue
            subm = self.profile_menu.addMenu(f"{cat_name} ({len(matching)})")
            for key in sorted(matching, key=lambda k: self.profiles[k]["name"]):
                name = self.profiles[key]["name"]
                act = QAction(name, subm, checkable=True)
                act.setChecked(key == self.audio_ctrl.profile)
                act.triggered.connect(lambda checked, k=key: self.on_profile_selected(k))
                self.profile_group.addAction(act)
                subm.addAction(act)
                self.profile_actions[key] = act
            
        # Monitored Drives Submenu
        self.drives_menu = self.menu.addMenu("Monitored Drives")
        self.update_drives_menu()
        
        # Volume Submenu
        self.vol_menu = self.menu.addMenu("Volume")
        vol_group = QActionGroup(self)
        for vol_pct in [25, 50, 75, 100]:
            act = QAction(f"{vol_pct}%", self.vol_menu, checkable=True)
            if vol_pct == int(self.audio_ctrl.volume * 100):
                act.setChecked(True)
            act.triggered.connect(lambda checked, v=vol_pct/100.0: self.audio_ctrl.set_volume(v))
            vol_group.addAction(act)
            self.vol_menu.addAction(act)
            
        # Sensitivity / Polling Submenu
        self.sens_menu = self.menu.addMenu("Sensitivity (Polling Rate)")
        sens_group = QActionGroup(self)
        sens_options = [
            (25, "Ultra Responsive (25ms)"),
            (45, "Balanced (45ms - Default)"),
            (100, "Eco / Low CPU (100ms)")
        ]
        for ms, label in sens_options:
            act = QAction(label, self.sens_menu, checkable=True)
            if ms == self.monitor.poll_interval_ms:
                act.setChecked(True)
            act.triggered.connect(lambda checked, m=ms: self.monitor.set_interval(m))
            sens_group.addAction(act)
            self.sens_menu.addAction(act)
            
        # Audio Engine Submenu
        self.engine_menu = self.menu.addMenu("Audio Backend")
        eng_group = QActionGroup(self)
        eng_qt = QAction("PyQt6 QtMultimedia (Multi-Voice Pool)", self.engine_menu, checkable=True)
        eng_qt.setChecked(self.audio_ctrl.engine == "qt")
        eng_qt.triggered.connect(lambda: setattr(self.audio_ctrl, "engine", "qt"))
        
        eng_pa = QAction("PulseAudio / PipeWire (paplay)", self.engine_menu, checkable=True)
        eng_pa.setChecked(self.audio_ctrl.engine == "paplay")
        eng_pa.triggered.connect(lambda: setattr(self.audio_ctrl, "engine", "paplay"))
        
        eng_group.addAction(eng_qt)
        eng_group.addAction(eng_pa)
        self.engine_menu.addAction(eng_qt)
        self.engine_menu.addAction(eng_pa)
        
        self.menu.addSeparator()
        
        # Test Click
        act_test = QAction("Simulate Test Click", self.menu)
        act_test.triggered.connect(lambda: self.audio_ctrl.play("crunch"))
        self.menu.addAction(act_test)
        
        # Settings Dashboard
        act_stats = QAction("Sound Selector & Settings Dashboard...", self.menu)
        act_stats.triggered.connect(self.show_settings)
        self.menu.addAction(act_stats)
        
        self.menu.addSeparator()
        
        # Quit
        act_quit = QAction("Quit Retro HDD Clicker", self.menu)
        act_quit.triggered.connect(self.quit)
        self.menu.addAction(act_quit)
        
        self.tray_icon.setContextMenu(self.menu)

    def on_profile_selected(self, profile_key):
        self.audio_ctrl.load_profile(profile_key)
        # Update check marks in menu
        if profile_key in self.profile_actions:
            self.profile_actions[profile_key].setChecked(True)
        if self.settings_dlg and self.settings_dlg.isVisible():
            self.settings_dlg.populate_list()

    def update_drives_menu(self):
        self.drives_menu.clear()
        for dev in self.available_drives:
            act = QAction(dev, self.drives_menu, checkable=True)
            act.setChecked(dev in self.monitor.monitored_drives)
            act.triggered.connect(lambda checked, d=dev: self.toggle_drive(d, checked))
            self.drives_menu.addAction(act)
        self.drives_menu.addSeparator()
        act_refresh = QAction("Refresh Drive List", self.drives_menu)
        act_refresh.triggered.connect(self.refresh_drives)
        self.drives_menu.addAction(act_refresh)

    def toggle_drive(self, dev, checked):
        if checked:
            self.monitor.monitored_drives.add(dev)
        else:
            self.monitor.monitored_drives.discard(dev)

    def refresh_drives(self):
        self.available_drives = self.discover_drives()
        self.update_drives_menu()

    def toggle_enable(self, checked):
        self.monitor.enabled = checked
        if checked:
            self.tray_icon.setIcon(self.icon_idle)
            self.tray_icon.setToolTip("Retro 90s HDD Clicker (Active)")
        else:
            self.tray_icon.setIcon(self.icon_disabled)
            self.tray_icon.setToolTip("Retro 90s HDD Clicker (Disabled)")

    def on_activity(self, sound_type, delta_magnitude):
        if not self.monitor.enabled:
            return
        self.audio_ctrl.play(sound_type)
        self.tray_icon.setIcon(self.icon_active)
        self.icon_reset_timer.start(80)

    def reset_tray_icon(self):
        if self.monitor.enabled:
            self.tray_icon.setIcon(self.icon_idle)
        else:
            self.tray_icon.setIcon(self.icon_disabled)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings()

    def show_settings(self):
        if not self.settings_dlg:
            self.settings_dlg = SettingsDialog(
                self.monitor,
                self.audio_ctrl,
                self.profiles,
                on_profile_changed_cb=self.on_profile_selected
            )
        self.settings_dlg.show()
        self.settings_dlg.raise_()
        self.settings_dlg.activateWindow()

if __name__ == "__main__":
    app = RetroHDDClickerApp(sys.argv)
    sys.exit(app.exec())
