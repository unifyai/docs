import datetime
import time

import unify
import random

endpoints = ("gpt-4o@openai", "claude-3.5-sonnet@anthropic", "gemini-1.5-pro@vertex-ai")
topics = ("maths", "history", "biology")
questions = {
    "maths": "what is 1 + 1?",
    "history": "When was the Magna Carta signed?",
    "biology": "What is a cell?"
}
clients = [unify.Unify(ep, cache=True, traced=True) for ep in endpoints]

with unify.Project("Traffic", overwrite=True):
    while True:
        time.sleep(random.uniform(0, 0.5))
        topic = random.choice(topics)
        question = questions[topic]
        # simulating the derived column
        ts = datetime.datetime.utcnow()
        ts_rounded = ts - datetime.timedelta(minutes=ts.minute, seconds=ts.second % 5, microseconds=ts.microsecond)
        with unify.Log(timestamp_rounded=ts_rounded.isoformat()):
            # end simulation
            random.choice(clients).generate(question, tags=[topic])
