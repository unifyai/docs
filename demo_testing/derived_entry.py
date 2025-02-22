import unify
import random
random.seed(0)

unify.activate("derived_entry", overwrite=True)

for _ in range(20):
    x = random.randint(0, 100)
    y = random.randint(0, 100)
    unify.log(
        x=x,
        y=y,
        # length=(x**2 + y**2)**0.5
    )
