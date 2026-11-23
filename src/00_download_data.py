"""
Download the PhysioNet Long-Term AF Database (ltafdb).

We only download the small files we need:
  .hea  header      (sampling rate, length of recording)
  .atr  annotations (rhythm labels, e.g. where AF starts and stops)
  .qrs  beat times  (used later to compute RR intervals)

We skip the big .dat files (raw ECG waveform) because we don't need them.

Run from the repo root:
  python "src/00_download_data.py"
"""

from pathlib import Path

import wfdb

DATABASE = "ltafdb"
OUTPUT_DIR = Path("data") / DATABASE
EXTENSIONS = [".hea", ".atr", ".qrs"]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Ask PhysioNet for the list of record names (e.g. "00", "01", ...)
    records = wfdb.get_record_list(DATABASE)
    print(f"PhysioNet lists {len(records)} records in '{DATABASE}'")

    # Build the list of files to download, e.g. "00.hea", "00.atr", "00.qrs"
    files = []
    for record in records:
        for ext in EXTENSIONS:
            files.append(record + ext)

    print(f"Downloading {len(files)} files into {OUTPUT_DIR} ...")
    # overwrite=False means files we already have are skipped on a re-run
    wfdb.dl_files(DATABASE, str(OUTPUT_DIR), files, overwrite=False)

    # Count a record as downloaded only if all 3 of its files are present
    complete = []
    for record in records:
        all_present = True
        for ext in EXTENSIONS:
            if not (OUTPUT_DIR / (record + ext)).exists():
                all_present = False
        if all_present:
            complete.append(record)

    print(f"Done: {len(complete)} of {len(records)} records downloaded completely.")


if __name__ == "__main__":
    main()
