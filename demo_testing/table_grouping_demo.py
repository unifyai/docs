import unify
import random

unify.activate("table-grouping-demo", overwrite=True)

questions = [
    "What is the weather in Paris?",
    "What is the weather in Tokyo?",
    "What is the weather in London?",
]

sys_msgs = [
    "You are a helpful assistant",
    "You are a helpful weather assistant",
    "You are a helpful assistant that can use tools",
]


for with_tool in [True, False]:
    for sys_msg in sys_msgs:
        with unify.Experiment(), unify.Params(
            with_tool=with_tool,
            sys_msg=sys_msg,
        ):
            for i, question in enumerate(questions):
                unify.log(question=question, score=i * 0.25 + random.random() / 2)
