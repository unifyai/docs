import unify
unify.activate("params-demo", overwrite=True)
log = unify.log(
    params={
        "system_message": "You are a helpful assistant.",
        "tool_use": True,
        "temperature": 0.5,
    },
    question="What is the capital of France?",
    answer="The capital of France is Paris.",
    score=1.0
)
