import unify
unify 
import random
random.seed(0)

base_msg = "You are a helpful assistant."
for tool_use in [True, False]:
    for sys_msg in [
        base_msg,
        base_msg + " You can use tools.",
        base_msg + " You can use tools and search the web."
    ]:
        for example_idx in range(10):
            unify.log(
                tool_use=tool_use,
                sys_msg=sys_msg,
                example_idx=example_idx,
                score=random.uniform(0, 10)
            )
