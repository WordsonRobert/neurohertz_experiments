# P03 · Simulation: which instability metric tracks frequency jitter and not nuisances?

**Question.** On simulated EEG whose gamma-frequency jitter, 1/f slope, amplitude, burst duration, muscle and noise are set by hand, which candidate metric changes with jitter (and only jitter)?
**Type.** Pipeline validation. Simulated data only. The simulation was calibrated to pooled, label-free medians of ds004504.
**When / where.** Final run on the laptop, 14 Nov 2026 (`final/`); variants on the laptop, 13–14 Nov (`ablation_variants/`).

**What was run.**
1. `02b_calibrate_simulation.py` matched the simulator to ds004504's pooled medians: exponent 1.11, burst rate, burst duration, envelope CV.
2. `02_simulation_validation.py` swept jitter and five nuisance parameters, and scored each metric. Its **specificity** = effect of jitter ÷ largest nuisance effect. It was eligible only if its rank correlation with jitter was ≥ 0.9.

**Commands.**
```bash
python scripts/02b_calibrate_simulation.py --dataset ds004504
python scripts/02_simulation_validation.py --jobs 8
```
**Code.** `../../code/neurohertz_v2_frozen/scripts/02_simulation_validation.py`, `02b_calibrate_simulation.py`, `../../code/neurohertz_v2_frozen/nh/simulate.py`

| Output in `results/` | Content |
|---|---|
| `final/metric_selection.json` | Ranking of all metrics: specificity score, jitter correlation, eligibility |
| `final/sim_summary.csv`, `final/sim_long.csv` | Effect of each swept parameter on each metric (summary / per simulation) |
| `final/sim_sweeps.png` | Figure of the sweeps |
| `final/calibration.json`, `calibration_grid.csv` | Calibration target and grid |
| `ablation_variants/<variant>/` | The same ranking under each estimator / median / chunk setting |
