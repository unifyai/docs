import os
import json
import wget
import unify

unify.activate("MarkingAssistant")

if not os.path.exists("usage_data.json"):
    breakpoint()
    wget.download(
        "https://github.com/unifyai/demos/"
        "raw/refs/heads/main/marking_assistant/"
        "data/usage_data.json"
    )

with open("usage_data.json", "r") as f:
    usage_data = json.load(f)

for i in range(31, 40):
    unify.create_logs(entries=usage_data[i*250:i*250+250])
