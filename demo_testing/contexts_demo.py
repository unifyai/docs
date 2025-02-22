import unify
import random
unify.activate("contexts_demo", overwrite=True)

names = ["Zoe", "John", "Jane", "Jim", "Jill"]
qnas = {
    "what is 1 + 1?": 2,
    "what is 2 * 3?": 6,
    "what is 3 - 2?": 1,
    "what is 4 / 2?": 2,
    "what is 5 % 2?": 1
}
regions = ["US", "EU", "UK", "AU", "CA"]

for _ in range(20):
    question, answer = random.choice(
        list(qnas.items())
    )
    unify.log(
        name=random.choice(names),
        question=question,
        answer=answer,
        region=random.choice(regions),
        context="Traffic"
)

predictions = [
    "six", "one", "two", "three", "four", "five"
]

for _ in range(15):
    question, answer = random.choice(
        list(qnas.items())
    )
    unify.log(
        name=random.choice(names),
        question=question,
        prediction=random.choice(
            predictions
        ),
        answer=answer,
        context="Evals"
    )
