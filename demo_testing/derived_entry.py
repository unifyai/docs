import unify
import random

random.seed(0)

unify.activate("derived_entry", overwrite=True)

for _ in range(20):
    x = random.random()
    y = random.random()
    unify.log(
        x0=x,
        x1=y,
        # length=(x**2 + y**2)**0.5
    )
