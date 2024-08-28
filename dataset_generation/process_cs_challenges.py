import json

with open("syllabus/cs_challenges.txt") as f:
    lines = f.readlines()

samples = []
cur_example = []
for l in lines:
    if not l.strip():
        samples.append("\n".join(cur_example))
        cur_example = []
    else:
        cur_example.append(l)

samples.append("\n".join(cur_example))


with open("dataset/cs_challenges.jsonl", "a") as f:
    for s in samples:
        d = {"prompt": f"Write a code solution to the following question\n{s}"}
        f.write(json.dumps(d)+"\n")
