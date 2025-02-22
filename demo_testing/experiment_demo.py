import unify
import random
unify.activate("experiments-demo")
with unify.Experiment(-1, overwrite=True), unify.Params(
    sys_msg="You are a helpful assistant."
):
    for _ in range(5):
        unify.log(
            question_number=random.randint(1, 20),
            score=random.random()
        )
