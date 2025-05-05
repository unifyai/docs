import unify

unify.activate("context-demo", overwrite=True)
unify.log(name="Zoe", question="what is 1 + 1?", region="US", context="Sciences/Maths")
unify.log(
    name="John",
    question="what is the speed of light?",
    region="EU",
    context="Sciences/Physics",
)
unify.log(
    name="Jane",
    question="What does this sentence convey?",
    region="UK",
    context="Arts/Literature",
)
