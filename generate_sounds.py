#!/usr/bin/env python3
import wave
import math
import struct
import random
import os

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)

PROFILES = {
    "caviar": {
        "name": "Western Digital Caviar (1995)",
        "freq_high": (3200, 3600),
        "freq_low": (380, 440),
        "decay_high": (160, 190),
        "decay_low": (60, 75),
        "noise_mix": 0.35,
        "step_duration": (18, 24),
    },
    "fireball": {
        "name": "Quantum Fireball (1998)",
        "freq_high": (3800, 4400),
        "freq_low": (460, 550),
        "decay_high": (190, 230),
        "decay_low": (70, 90),
        "noise_mix": 0.45,
        "step_duration": (14, 20),
    },
    "deskstar": {
        "name": "IBM Deskstar 75GXP (2000)",
        "freq_high": (2600, 3100),
        "freq_low": (310, 380),
        "decay_high": (130, 160),
        "decay_low": (50, 65),
        "noise_mix": 0.30,
        "step_duration": (22, 28),
    },
    "medalist": {
        "name": "Seagate Medalist (1993)",
        "freq_high": (3000, 3400),
        "freq_low": (350, 410),
        "decay_high": (145, 175),
        "decay_low": (55, 70),
        "noise_mix": 0.38,
        "step_duration": (20, 26),
    }
}

def generate_seek_impulse(length_ms, freq_high, freq_low, decay_high, decay_low, noise_mix, volume=0.75):
    sample_rate = 44100
    num_samples = int(sample_rate * length_ms / 1000)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        high = math.sin(2 * math.pi * freq_high * t) * math.exp(-t * decay_high)
        low = math.sin(2 * math.pi * freq_low * t) * math.exp(-t * decay_low)
        noise = (random.random() * 2 - 1) * math.exp(-t * (decay_high * 1.5))
        
        sample = (high * 0.45 + low * 0.4 + noise * noise_mix) * volume
        sample = max(-1.0, min(1.0, sample * 1.25))
        samples.append(int(sample * 32767))
    return samples

def write_wav(filename, sample_list):
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        data = struct.pack('<' + 'h'*len(sample_list), *sample_list)
        w.writeframesraw(data)

def build_profile(profile_key, cfg):
    profile_dir = os.path.join(SOUNDS_DIR, profile_key)
    os.makedirs(profile_dir, exist_ok=True)
    
    # 1. Single Seek
    fh = random.uniform(*cfg["freq_high"])
    fl = random.uniform(*cfg["freq_low"])
    dh = random.uniform(*cfg["decay_high"])
    dl = random.uniform(*cfg["decay_low"])
    dur = random.uniform(*cfg["step_duration"])
    single = generate_seek_impulse(dur, fh, fl, dh, dl, cfg["noise_mix"], volume=0.78)
    write_wav(os.path.join(profile_dir, "single.wav"), single)
    
    # 2. Double Seek
    fh1 = random.uniform(*cfg["freq_high"])
    fl1 = random.uniform(*cfg["freq_low"])
    s1 = generate_seek_impulse(dur * 0.9, fh1, fl1, dh, dl, cfg["noise_mix"], volume=0.76)
    silence = [0] * int(44100 * 0.015)
    fh2 = random.uniform(*cfg["freq_high"]) * 1.05
    fl2 = random.uniform(*cfg["freq_low"]) * 1.03
    s2 = generate_seek_impulse(dur * 1.1, fh2, fl2, dh, dl, cfg["noise_mix"], volume=0.76)
    write_wav(os.path.join(profile_dir, "double.wav"), s1 + silence + s2)
    
    # 3. Heavy Crunch
    crunch = []
    num_steps = random.randint(5, 7)
    for i in range(num_steps):
        fh_step = random.uniform(*cfg["freq_high"])
        fl_step = random.uniform(*cfg["freq_low"])
        dh_step = random.uniform(*cfg["decay_high"])
        dl_step = random.uniform(*cfg["decay_low"])
        dur_step = random.uniform(*cfg["step_duration"])
        step = generate_seek_impulse(dur_step, fh_step, fl_step, dh_step, dl_step, cfg["noise_mix"], volume=random.uniform(0.70, 0.82))
        gap = [0] * int(44100 * random.uniform(0.003, 0.012))
        crunch.extend(step + gap)
    write_wav(os.path.join(profile_dir, "crunch.wav"), crunch)
    print(f"Generated profile '{profile_key}' ({cfg['name']}) -> {profile_dir}")

if __name__ == "__main__":
    for k, v in PROFILES.items():
        build_profile(k, v)
