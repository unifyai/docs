# ---
# title: 'Usage Dashboard'
# ---

# Let's assume our app has been deployed for a few weeks now,
# and we've been tracking the daily usage coming from ~100 active users.
# For now, the students answer the questions,
# and then a **human** marks the questions asynchronously,
# but this is both timely and expensive.

# Firt things first, let's add the necessary imports...

# ```python
import os
import json
import wget
import unify
# ```

# ...and activate our project.

# ```python
unify.activate("MarkingAssistant")
# ```

# We have the usage data exported to [usage_data.json](https://github.com/unifyai/demos/blob/main/marking_assistant/data/usage_data.json).
# Let's first download this file.

# ```python
if not os.path.exists("usage_data.json"):
    wget.download(
        "https://github.com/unifyai/demos/"
        "raw/refs/heads/main/marking_assistant/"
        "data/usage_data.json"
    )
# ``` 

# Let's now upload this production traffic into our new interface,
# to get a complete picture.
# This will take a few minutes,
# as there are 10,000 logs to upload.

# ```python
with open("usage_data.json", "r") as f:
    usage_data = json.load(f)

unify.create_logs(context="Usage", entries=usage_data)
# ```