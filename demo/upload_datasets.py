import os
import wget
import json
import unify

unify.activate("MarkingAssistant", overwrite=True)

# Users

if not os.path.exists("users.json"):
    wget.download(
        "https://github.com/unifyai/demos/"
        "raw/refs/heads/main/marking_assistant/"
        "data/users.json"
    )

with open("users.json", "r") as f:
    users = json.load(f)

users_dataset = unify.Dataset(users, name="Users")
users_dataset.sync()

# Test Set

if not os.path.exists("users.json"):
    wget.download(
        "https://github.com/unifyai/demos/"
        "raw/refs/heads/main/marking_assistant/"
        "data/test_set.json"
    )

with open("test_set.json", "r") as f:
    test_set = json.load(f)

test_set = unify.Dataset(test_set, name="TestSet")
test_set.sync()

# Sub Test Sets


for size in [10, 20, 40, 80, 160]:
    unify.Dataset(test_set[0:size].data).set_name(f"TestSet{size}").sync()
