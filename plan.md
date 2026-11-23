# 6-Day Plan — af-hrv-ml-practice

**Dates:** 24–29 November 2026
**Goal:** real AF data → RR intervals → HRV features → patient-level split → model → honest evaluation
**Data:** PhysioNet Long-Term AF Database (LTAFDB), 84 records, ~24 h each

---

## Daily routine

| Block | Time | What |
|-------|------|------|
| Heart study | ~1 h | Main task (Fujiwara-sensei's instruction) |
| Project | ~1–1.5 h | Claude Code writes, **I check every step** |
| Learn | ~20 min | Write 3 lines in `notes/`: what we did, why, what I'd check |
| Japanese | 15 min | Every day |

---

## Day 1 — Explore the data (24 Nov)

- **Heart study:** AF — why the rhythm becomes irregular
- **Project:** `src/01_explore.py` — load 1 record → RR intervals → plot with AF episodes marked
- **Check:** Can I *see* AF in the plot?

- [ ] Heart study
- [ ] Script runs + plot looks right
- [ ] Notes written

## Day 2 — Clean + windows (25 Nov)

- **Heart study:** Other arrhythmias + ectopic beats
- **Project:** `src/02_clean_windows.py` — remove impossible RR intervals, cut into 30-beat windows, label each window AF / non-AF
- **Check:** How many windows in total? How many AF?

- [ ] Heart study
- [ ] Script runs + counts make sense
- [ ] Notes written

## Day 3 — Features (26 Nov)

- **Heart study:** HRV paper — time-domain metrics
- **Project:** `src/03_features.py` — mean RR, SDNN, RMSSD, pNN50 per window → one table with a patient ID column
- **Check:** Are SDNN and RMSSD higher in AF windows?

- [ ] Heart study
- [ ] Feature table built
- [ ] Notes written

## Day 4 — Split + first model (27 Nov)

- **Heart study:** Catheter ablation
- **Project:** `src/04_train.py` — split **by patient** → baseline → decision tree
- **Check:** Is any patient in both train and test? (Must be **no**)

- [ ] Heart study
- [ ] Patient-level split verified
- [ ] Tree beats baseline
- [ ] Notes written

## Day 5 — XGBoost + evaluation (28 Nov)

- **Heart study:** HRV changes after ablation
- **Project:** `src/05_evaluate.py` — XGBoost + random undersampling → confusion matrix, sensitivity, overlooking rate
- **Check:** Did it beat the baseline? How many AF windows were missed?

- [ ] Heart study
- [ ] Metrics reported
- [ ] Notes written

## Day 6 — Write-up (29 Nov)

- **Heart study:** Re-read the lab paper
- **Project:** `README.md` — what I built, results, what I learned
- **Check:** Could I explain this to Saeda-sensei?

- [ ] Lab paper re-read
- [ ] README written

---

**30 Nov:** rest / buffer — lab dataset expected

## Notes

- This dataset gives **AF vs non-AF** (2 classes). The lab uses 3 classes, but the pipeline is the same.
- The 30-beat windows copy the lab paper's setup on purpose.
- If a day runs over, push the rest along. Heart study comes first.
- Simulated or public data only. Never commit lab data.