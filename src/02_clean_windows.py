"""
Day 2: clean RR intervals and cut them into 30-beat windows (all 84 records).

For every record:
  1. read the reference beats (.atr) and make RR intervals in seconds
  2. give every RR interval the rhythm active at that time ("(AFIB", "(N", ...)
  3. cut into non-overlapping windows of 30 RR intervals
  4. drop windows with impossible RR, unknown rhythm, or mixed AF / non-AF
  5. label the rest "AF" or "non-AF"

Output: data/processed/windows.csv (one row per window)
        outputs/02_example_windows.png

Note: read the CSV with pd.read_csv(path, dtype={"record": str}),
otherwise record IDs like "00" and "01" turn into the numbers 0 and 1.

Run from the repo root:
  python "src/02_clean_windows.py"
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import wfdb

# ---------------------------------------------------------------
# Settings
# ---------------------------------------------------------------
DATA_DIR = Path("data") / "ltafdb"
PROCESSED_DIR = Path("data") / "processed"
OUTPUT_DIR = Path("outputs")

WINDOW_SIZE = 30      # RR intervals per window (copies the lab paper)
RR_MIN = 0.3          # seconds (= 200 beats per minute)
RR_MAX = 2.0          # seconds (= 30 beats per minute)
RANDOM_STATE = 42     # for picking example windows to plot

# Annotation symbols that are real heartbeats (same as Day 1).
# Skips non-beat markers like "+" (rhythm change) and '"' (comment).
BEAT_SYMBOLS = {"N", "L", "R", "B", "A", "a", "J", "S", "V",
                "r", "F", "e", "j", "n", "E", "/", "f", "Q", "?"}


# ---------------------------------------------------------------
# Functions: one record -> RR intervals with rhythm labels
# ---------------------------------------------------------------
def list_records():
    """Record names that have an .atr file, e.g. ["00", "01", ...]."""
    names = []
    for path in sorted(DATA_DIR.glob("*.atr")):
        names.append(path.stem)
    return names


def load_annotations(record):
    """Read the .atr file. Returns sample positions, symbols, aux notes, fs."""
    annotation = wfdb.rdann(str(DATA_DIR / record), "atr")
    samples = np.array(annotation.sample)
    symbols = np.array(annotation.symbol)
    aux_notes = []
    for note in annotation.aux_note:
        aux_notes.append(note.strip("\x00"))
    return samples, symbols, aux_notes, annotation.fs


def get_rr_intervals(samples, symbols, fs):
    """Keep only real beats, return RR intervals (s) and the time of each RR's end beat (s)."""
    is_beat = np.isin(symbols, list(BEAT_SYMBOLS))
    beat_times = samples[is_beat] / fs
    rr = np.diff(beat_times)
    rr_end_times = beat_times[1:]     # each RR gets the time of the beat that ends it
    return rr, rr_end_times


def get_rhythm_changes(samples, aux_notes, fs):
    """Rhythm labels like "(AFIB" as two arrays: times (s) and rhythm names."""
    times = []
    rhythms = []
    for sample, note in zip(samples, aux_notes):
        if note.startswith("("):
            times.append(sample / fs)
            rhythms.append(note)
    return np.array(times), np.array(rhythms)


def label_each_rr(rr_end_times, change_times, change_rhythms):
    """Give each RR interval the rhythm active at its end beat.

    The active rhythm is the most recent label at or before that time.
    RR intervals before the first rhythm label get "unknown".
    """
    # searchsorted finds, for each time, how many labels come at or before it.
    # Subtracting 1 gives the index of the most recent label (-1 = none yet).
    label_index = np.searchsorted(change_times, rr_end_times, side="right") - 1

    rr_rhythms = []
    for index in label_index:
        if index < 0:
            rr_rhythms.append("unknown")
        else:
            rr_rhythms.append(change_rhythms[index])
    return np.array(rr_rhythms)


# ---------------------------------------------------------------
# Functions: RR intervals -> clean, labelled windows
# ---------------------------------------------------------------
def classify_window(rr_window, rhythm_window):
    """Return "AF", "non-AF", or a drop reason for one window.

    Checks run in order, so each dropped window is counted once:
    impossible RR first, then unknown rhythm, then mixed.
    """
    if np.any(rr_window < RR_MIN) or np.any(rr_window > RR_MAX):
        return "drop_impossible_rr"
    if np.any(rhythm_window == "unknown"):
        return "drop_unknown"
    is_af = rhythm_window == "(AFIB"
    if np.all(is_af):
        return "AF"
    if not np.any(is_af):
        return "non-AF"
    return "drop_mixed"


def make_windows(record, rr, rr_end_times, rr_rhythms):
    """Cut one record into non-overlapping windows of WINDOW_SIZE RR intervals.

    Returns (kept_rows, drop_counts). Leftover RR at the end (< 30) is ignored.
    """
    kept_rows = []
    drop_counts = {"drop_impossible_rr": 0, "drop_unknown": 0, "drop_mixed": 0}

    n_windows = len(rr) // WINDOW_SIZE
    for w in range(n_windows):
        start = w * WINDOW_SIZE
        end = start + WINDOW_SIZE
        rr_window = rr[start:end]
        result = classify_window(rr_window, rr_rhythms[start:end])

        if result in drop_counts:
            drop_counts[result] += 1
            continue

        # Start time = time of the beat where the first RR interval begins
        row = {"record": record,
               "start_time_s": round(rr_end_times[start] - rr_window[0], 3)}
        for i in range(WINDOW_SIZE):
            row[f"rr_{i + 1}"] = round(rr_window[i], 4)
        row["label"] = result
        kept_rows.append(row)

    return kept_rows, drop_counts


def process_record(record):
    """Run the full Day 2 steps for one record."""
    samples, symbols, aux_notes, fs = load_annotations(record)
    rr, rr_end_times = get_rr_intervals(samples, symbols, fs)
    change_times, change_rhythms = get_rhythm_changes(samples, aux_notes, fs)
    rr_rhythms = label_each_rr(rr_end_times, change_times, change_rhythms)
    return make_windows(record, rr, rr_end_times, rr_rhythms)


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():
    records = list_records()
    print(f"Records found: {len(records)}")

    all_rows = []
    total_drops = {"drop_impossible_rr": 0, "drop_unknown": 0, "drop_mixed": 0}
    for record in records:
        rows, drops = process_record(record)
        all_rows.extend(rows)
        for reason in total_drops:
            total_drops[reason] += drops[reason]

    windows = pd.DataFrame(all_rows)
    print(f"Windows table shape: {windows.shape}  (rows = windows, columns = "
          f"record + start_time_s + {WINDOW_SIZE} RR + label)")

    # ---- Save ----
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = PROCESSED_DIR / "windows.csv"
    windows.to_csv(csv_path, index=False)
    print(f"Saved {csv_path}")

    # ---- Report ----
    n_dropped = sum(total_drops.values())
    n_total = len(windows) + n_dropped
    print(f"\nWindows cut: {n_total}")
    print(f"  kept:                 {len(windows)}")
    print(f"  dropped, impossible RR: {total_drops['drop_impossible_rr']}")
    print(f"  dropped, unknown:       {total_drops['drop_unknown']}")
    print(f"  dropped, mixed:         {total_drops['drop_mixed']}")

    counts = windows["label"].value_counts()
    n_af = counts.get("AF", 0)
    n_non_af = counts.get("non-AF", 0)
    print(f"\nAF windows:     {n_af}")
    print(f"non-AF windows: {n_non_af}")
    print(f"% AF:           {100 * n_af / len(windows):.1f}%")

    records_with_af = windows.loc[windows["label"] == "AF", "record"].nunique()
    print(f"\nRecords with at least one AF window: {records_with_af} of {len(records)}")

    print("\nTop 5 records by number of windows:")
    print(windows["record"].value_counts().head(5).to_string())

    # ---- Plot one AF and one non-AF example window ----
    rr_columns = [f"rr_{i + 1}" for i in range(WINDOW_SIZE)]
    af_example = windows[windows["label"] == "AF"].sample(1, random_state=RANDOM_STATE).iloc[0]
    non_af_example = windows[windows["label"] == "non-AF"].sample(1, random_state=RANDOM_STATE).iloc[0]
    beat_numbers = np.arange(1, WINDOW_SIZE + 1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    examples = [(ax_left, non_af_example, "tab:blue"), (ax_right, af_example, "tab:red")]
    for ax, example, color in examples:
        ax.plot(beat_numbers, example[rr_columns].astype(float), marker="o", color=color)
        ax.set_title(f"{example['label']} window - record {example['record']}, "
                     f"start {example['start_time_s'] / 3600:.2f} h")
        ax.set_xlabel("Beat number in window")
        ax.grid(alpha=0.3)
    ax_left.set_ylabel("RR interval (seconds)")
    fig.suptitle("Example 30-beat windows: non-AF vs AF (same y-axis scale)")
    fig.tight_layout()
    plot_path = OUTPUT_DIR / "02_example_windows.png"
    fig.savefig(plot_path, dpi=150)
    print(f"\nSaved {plot_path}")
    plt.show()


if __name__ == "__main__":
    main()
