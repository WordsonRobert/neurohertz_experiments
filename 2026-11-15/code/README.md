# Code

| Folder | What it is | Produced |
|---|---|---|
| `neurohertz_v2_frozen/` | The frozen pipeline exactly as hashed at the freeze (code hash `5ab5a4a7…`, see `pipeline_validation/P09/results/freeze.json`) | P01–P09, H1–H6 |
| `classification_sweep/` | The exploratory sweep (stages 00–60) plus the existing-feature analysis (`explore/01_existing_features.py`) | H7, H8, H9, P10 |
| `colab/` | Colab notebooks used for the first runs and data inspection; `run_laptop_ablations.sh` (laptop ablations) | P02, P03 |

## Running the frozen pipeline

```bash
cd neurohertz_v2_frozen
pip install -r requirements.txt
python -m pytest -q          # 55 tests
bash run_final.sh            # full run; edit config/datasets.yaml so `roots` point to your ds004504 / ds006036 copies
```

`run_final.sh` lists every step in order, with a comment on each. `docs/ANALYSIS_PLAN.md` is the pre-registered plan, `docs/LEAKAGE_CONTRACT.md` lists the rules that keep labels out of label-free steps, `docs/MECHANISMS.md` lists the mechanism theories, and `docs/METHODS_REVIEW.md` records the method decisions.

## Running the classification sweep

The sweep imports the frozen code read-only. It expects this layout:
```
<parent>/final_run/neurohertz_v2/   (= neurohertz_v2_frozen)
<parent>/classification/            (= classification_sweep)
```
Then run `bash run_classification.sh` (about 3–4 h with 8 cores). Set `NH_CODE` to point elsewhere. `docs/HYPOTHESIS_TREE.md` explains each stage's purpose.
