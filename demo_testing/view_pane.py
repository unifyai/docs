import unify

unify.activate("llm-trace-demo", overwrite=True)


@unify.traced
def llm_jury(question):
    a1 = unify.Unify("o3-mini@openai", traced=True).generate(question)
    a2 = unify.Unify("deepseek-r1@together-ai", traced=True).generate(question)
    return unify.Unify("gpt-4o@openai", traced=True).generate(
        f"Summarize the following: {a1} {a2}"
    )


llm_jury("What is the capital of France?")
