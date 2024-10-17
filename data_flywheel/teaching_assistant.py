import time

import unify


# Iteration 1 #
# ------------#

# define client
client = unify.Unify("gpt-4o@openai", cache=True)

# first set of questions
qs = ["3 - 1", "4 + 7", "6 + 2", "9 - 3", "7 + 9"]


# scorer
def evaluate_response(question: str, response: str) -> float:
    correct_answer = eval(question)
    try:
        response_int = int(
            "".join([c for c in response.split(" ")[-1] if c.isdigit()]),
        )
        return float(correct_answer == response_int)
    except ValueError:
        return 0.


# scores
scores = [evaluate_response(q, client.generate(q)) for q in qs]
print(scores)


# Iteration 2 #
# ------------#

from random import randint, choice, seed
seed(0)
qs += [f"{randint(0, 100)} {choice(['+', '-'])} {randint(0, 100)}" for i in range(25)]

t0 = time.perf_counter()
scores = [evaluate_response(q, client.generate(q)) for q in qs]
print(f"serial scoring took {time.perf_counter() - t0} seconds")
print(f"{int(sum(scores))}/{len(scores)} correct")


def evaluate(q: str):
    response = client.generate(q)
    return evaluate_response(q, response)


client.set_cache(False)

t0 = time.perf_counter()
scores = unify.map(evaluate, qs)
print(f"mapping wo cache took {time.perf_counter() - t0} seconds")

client.set_cache(True)

t0 = time.perf_counter()
scores = unify.map(evaluate, qs)
print(f"mapping w cache took {time.perf_counter() - t0} seconds")

print(f"{int(sum(scores))}/{len(scores)} correct")

unify.activate("maths_assistant")

def evaluate(q: str):
    response = client.generate(q)
    score = evaluate_response(q, response)
    return unify.log(
        question=q,
        response=response,
        score=score
    )


logs = unify.map(evaluate, qs)


# Iteration 3 #
# ------------#
