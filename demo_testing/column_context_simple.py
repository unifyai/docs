import unify
unify.activate("sciences", overwrite=True)
with unify.Log(), unify.ColumnContext("Sciences"):
    with unify.ColumnContext("Maths"):
        unify.log(
            name="Zoe",
            question="what is 1 + 1?",
            region="US"
        )
    with unify.ColumnContext("Physics"):
        unify.log(
            name="John",
            question="what is the speed of light?",
            region="EU"
        )
