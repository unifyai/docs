import unify
import random

unify.activate("derived-columns-demo", overwrite=True)

for _ in range(20):
    unify.log(x=random.random(), y=random.random())
