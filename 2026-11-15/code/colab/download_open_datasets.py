# NeuroHertz: download the open OpenNeuro datasets straight into Google Drive from Colab.
# Uses the public OpenNeuro S3 bucket (no account needed). Writing to Drive is slow for
# many small files, so we sync to local Colab disk first, then copy to Drive in one go.
# Turn datasets on/off in WANT. Sizes are rough; check free Drive space first (you have ~50 GB).

# %% [1] setup
import os, subprocess, sys
from google.colab import drive
drive.mount("/content/drive")
subprocess.run("pip -q install awscli", shell=True)
DEST = "/content/drive/MyDrive/datasets"
os.makedirs(DEST, exist_ok=True)

WANT = {
    # accession : (why, extra aws sync args)
    "ds004504": ("discovery: AD/FTD/CN eyes closed (incl. derivatives/)", ""),
    "ds006036": ("same 88 people, eyes open + photic", ""),
    "ds007427": ("Colombia: CN/MCI/AD + PSEN1 carriers (lockbox)", ""),
    "ds005048": ("Tehran 40 Hz auditory: AD/MCI/CN (lockbox + perturbation)", ""),
    "ds004796": ("PEARL-Neuro: APOE risk, healthy 50-63 (rest only)", '--exclude "*" --include "participants.*" --include "*task-rest*"'),
    "ds004148": ("test-retest healthy, 3 sessions (rest only)",
                 '--exclude "*" --include "participants.*" --include "*rest*" --include "*eyes*" --include "*EC*" --include "*EO*"'),
    # "ds005385": ("Dortmund Vital: lifespan norms + 5-yr follow-up", ""),  # VERY large (608 people x 4 recordings
    #   at 1000 Hz): likely bigger than your free Drive space. Download a subset later.
}

# %% [2] download (one at a time; re-run is safe, sync skips finished files)
for acc, (why, extra) in WANT.items():
    local = f"/content/tmp_{acc}"
    print(f"\n=== {acc}: {why}")
    subprocess.run(f'aws s3 sync --no-sign-request s3://openneuro.org/{acc} {local} {extra}', shell=True)
    subprocess.run(f'rsync -a {local}/ "{DEST}/{acc}/" && rm -rf {local}', shell=True)
    subprocess.run(f'du -sh "{DEST}/{acc}"', shell=True)

# CAUEEG (request form + ethics approval) and BrainLat (Synapse data-use agreement) cannot be
# downloaded anonymously; put them under MyDrive/datasets/<name>/ once access is granted.
