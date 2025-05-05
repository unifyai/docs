import unify

unify.activate("bar-chart-grouped", overwrite=True)
import random

random.seed(0)

base_msg = "You are a helpful assistant."
for tool_use in [True, False]:
    with unify.Params(tool_use=tool_use):
        for i, sys_msg in enumerate(
            [
                base_msg,
                base_msg + " You can use tools.",
                base_msg + " You can use tools and search the web.",
            ]
        ):
            with unify.Params(sys_msg=sys_msg):
                for example_idx in range(10):
                    unify.log(
                        example_idx=example_idx,
                        score=random.uniform(0, 10),
                        experiment="tool_use:" + str(tool_use) + ",sys_msg:" + str(i),
                    )
