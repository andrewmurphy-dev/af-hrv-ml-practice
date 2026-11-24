"""
Day 1: explore one LTAFDB record.

Loads the reference beat annotations (.atr), turns them into RR intervals,
finds the AF episodes, and plots RR over time with AF shaded.

Run from the repo root:
  python "src/01_explore.py"
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import wfdb

# ---------------------------------------------------------------
# Settings
# ---------------------------------------------------------------
RECORD = "111"
RECORD_PATH = str(Path("data") / "ltafdb" / RECORD)
OUTPUT_DIR = Path("outputs")

# Annotation symbols that are real heartbeats.
# The .atr file also has non-beat markers we must skip:
#   "+" = rhythm change, '"' = comment, "~" = noise, etc.
BEAT_SYMBOLS = {"N", "L", "R", "B", "A", "a", "J", "S", "V",
                "r", "F", "e", "j", "n", "E", "/", "f", "Q", "?"}

# Limits for a "possible" RR interval (checked only, not removed today)
RR_MIN = 0.3  # seconds (= 200 beats per minute)
RR_MAX = 2.0  # seconds (= 30 beats per minute)

# ---------------------------------------------------------------
# 1. Load the header and annotations
# ---------------------------------------------------------------
header = wfdb.rdheader(RECORD_PATH)
fs = header.fs                                # samples per second
recording_seconds = header.sig_len / fs

annotation = wfdb.rdann(RECORD_PATH, "atr")
samples = np.array(annotation.sample)         # position of each annotation
symbols = np.array(annotation.symbol)         # beat type or "+" etc.
aux_notes = [note.strip("\x00") for note in annotation.aux_note]

print(f"Record {RECORD}: sampling rate = {fs} Hz, "
      f"length = {recording_seconds / 3600:.2f} hours")
print(f"Annotations loaded: {len(samples)}")

# ---------------------------------------------------------------
# 2. Beats -> RR intervals
# ---------------------------------------------------------------
is_beat = np.isin(symbols, list(BEAT_SYMBOLS))
beat_samples = samples[is_beat]
beat_times = beat_samples / fs                # seconds from start

# RR interval = time between one beat and the next
rr = np.diff(beat_times)
# Give each RR interval the time of the beat that ends it
rr_times = beat_times[1:]

print(f"\nBeats: {len(beat_times)}")
print(f"RR intervals: {len(rr)}  (shape {rr.shape})")
print(f"RR mean = {rr.mean():.3f} s, min = {rr.min():.3f} s, max = {rr.max():.3f} s")

# ---------------------------------------------------------------
# 3. Rhythm labels -> AF episodes
# ---------------------------------------------------------------
# A rhythm label like "(AFIB" means "from here on, the rhythm is AF",
# until the next rhythm label. So we collect (start time, rhythm) pairs.
rhythm_changes = []
for sample, note in zip(samples, aux_notes):
    if note.startswith("("):
        rhythm_changes.append((sample / fs, note))

# Turn them into AF episodes: (start, end) in seconds.
# Back-to-back "(AFIB" labels are merged into one episode.
af_episodes = []
af_start = None
for time, rhythm in rhythm_changes:
    if rhythm == "(AFIB" and af_start is None:
        af_start = time                       # AF begins
    elif rhythm != "(AFIB" and af_start is not None:
        af_episodes.append((af_start, time))  # AF ends
        af_start = None
if af_start is not None:                      # AF lasts until the end
    af_episodes.append((af_start, recording_seconds))

af_seconds = 0.0
for start, end in af_episodes:
    af_seconds += end - start
af_percent = 100 * af_seconds / recording_seconds

print(f"\nRhythm labels: {len(rhythm_changes)}")
print(f"AF episodes: {len(af_episodes)}")
print(f"AF time: {af_seconds / 3600:.2f} hours = {af_percent:.1f}% of the recording")

# ---------------------------------------------------------------
# 4. Plot: full recording
# ---------------------------------------------------------------
OUTPUT_DIR.mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(rr_times / 3600, rr, linewidth=0.3, color="tab:blue", label="RR interval")
for i, (start, end) in enumerate(af_episodes):
    # Only label the first shaded area, so the legend has one "AF" entry
    label = "AF episode" if i == 0 else None
    ax.axvspan(start / 3600, end / 3600, color="tab:red", alpha=0.2, label=label)
ax.set_title(f"LTAFDB record {RECORD}: RR intervals with AF episodes shaded")
ax.set_xlabel("Time (hours)")
ax.set_ylabel("RR interval (seconds)")
ax.set_ylim(0, 2.5)
ax.legend(loc="upper right")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "01_rr_af.png", dpi=150)
print(f"\nSaved {OUTPUT_DIR / '01_rr_af.png'}")

# ---------------------------------------------------------------
# 5. Plot: 10-minute zoom around one AF start
# ---------------------------------------------------------------
# Use the start of the longest AF episode, so we see a clear switch
longest = max(af_episodes, key=lambda episode: episode[1] - episode[0])
zoom_center = longest[0]
zoom_start = zoom_center - 5 * 60             # 5 minutes before
zoom_end = zoom_center + 5 * 60               # 5 minutes after

in_zoom = (rr_times >= zoom_start) & (rr_times <= zoom_end)
# Time in minutes relative to AF start (negative = before AF)
zoom_minutes = (rr_times[in_zoom] - zoom_center) / 60

fig2, ax2 = plt.subplots(figsize=(14, 5))
ax2.plot(zoom_minutes, rr[in_zoom], marker=".", markersize=3,
         linewidth=0.5, color="tab:blue", label="RR interval")
for i, (start, end) in enumerate(af_episodes):
    if end >= zoom_start and start <= zoom_end:
        shade_start = (max(start, zoom_start) - zoom_center) / 60
        shade_end = (min(end, zoom_end) - zoom_center) / 60
        label = "AF episode" if i == af_episodes.index(longest) else None
        ax2.axvspan(shade_start, shade_end, color="tab:red", alpha=0.2, label=label)
ax2.axvline(0, color="black", linestyle="--", linewidth=1, label="AF starts")
ax2.set_title(f"Record {RECORD}: 10 minutes around AF onset "
              f"at {zoom_center / 3600:.2f} h")
ax2.set_xlabel("Minutes relative to AF start")
ax2.set_ylabel("RR interval (seconds)")
ax2.legend(loc="upper right")
fig2.tight_layout()
fig2.savefig(OUTPUT_DIR / "01_rr_af_zoom.png", dpi=150)
print(f"Saved {OUTPUT_DIR / '01_rr_af_zoom.png'}")

# ---------------------------------------------------------------
# 6. Sanity check: impossible RR values (not removed yet - Day 2)
# ---------------------------------------------------------------
too_short = rr < RR_MIN
too_long = rr > RR_MAX
print(f"\nSanity check (RR outside {RR_MIN}-{RR_MAX} s):")
print(f"  under {RR_MIN} s: {too_short.sum()}")
print(f"  over  {RR_MAX} s: {too_long.sum()}")
print(f"  total: {(too_short | too_long).sum()} of {len(rr)} "
      f"({100 * (too_short | too_long).mean():.2f}%)")

plt.show()
