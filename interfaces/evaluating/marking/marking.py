import os
import wget
import json


# Download Ground Truth Data
fname = "data.json"
if not os.path.exists(fname):
    wget.download("https://raw.githubusercontent.com/unifyai/unify-docs/refs/heads/main/interfaces/ai_tutor/data/data.json")
with open(fname, "r") as f:
    data = json.load(f)

# Save as Dataset

import unify
with unify.Context("Datasets"):
    with unify.Context("Test Set"):
        unify.log([{"question": k, "scores_and_answers": v} for k, v in data.items()])
