import unify
import random

unify.activate("derived_entry")

for _ in range(20):
    unify.log(
        x=random.random(),
        y=random.random()
    )
