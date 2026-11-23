# CLAUDE.md — af-hrv-ml-practice

## About this project
- A practice sandbox for learning ML on heart rhythm data (RR intervals, HRV, AF).
- It mirrors the lab pipeline: RR intervals → HRV features → model → evaluation.
- SIMULATED OR PUBLIC DATA ONLY. Never add real lab data, lab scripts, or anything confidential.

## About me
- I'm a beginner in machine learning, but experienced in Python backend work (FastAPI, PostgreSQL).
- I learn best in small steps, with plain explanations and visuals.
- I want to understand the code, not just have it written for me.

## How to work with me
- Do ONE small step at a time, then stop and let me run it.
- Explain each step simply: what it does and why.
- Explain new terms the first time they appear. Prefer plain words over jargon.
- Don't write the whole pipeline in one go.
- Ask before big changes or new files.
- Keep code simple and readable, with short comments. No clever one-liners.
- When something can be shown, add a plot (matplotlib).

## ML rules (always follow)
- Use random_state=42 everywhere randomness is involved.
- Print shapes after loading and after splitting.
- Split BEFORE any scaling, imputing, or resampling.
- Fit scalers / imputers / resamplers on TRAIN ONLY, then transform train and test.
- Prefer a Pipeline so preprocessing can't leak.
- When data has patients, split BY PATIENT (e.g. GroupKFold). The same patient must never be in both train and test.
- Always build a simple baseline first, and compare the model against it.
- For AF / imbalanced data, report more than accuracy: confusion matrix, sensitivity (recall) for AF, and the overlooking rate (AF predicted as normal).
- If a score looks too good, say so and check for leakage.

## Environment
- Python virtual env in .venv (activate before running).
- Run files from the repo root with quotes, e.g.:
  python "src/01_simulate_rr.py"
- Main libraries: numpy, pandas, matplotlib, scikit-learn, xgboost.