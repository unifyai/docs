import unify
import random
unify.activate("params-demo", overwrite=True)
with unify.Params(
    system_message="You are a helpful assistant.",
):  
    for temperature in [0.5, 0.7]:
        with unify.Params(temperature=temperature):
            for tool_use in [False, True]:
                with unify.Params(tool_use=tool_use):
                    [unify.log(score=random.random()) for _ in range(2)]
