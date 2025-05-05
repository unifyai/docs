import unify

unify.activate("table-manipulation", overwrite=True)
unify.log(x=0, y={"a": [1, 2, 3]}, msg="hello", score=0.123)
unify.log(x=1, y={"b": [4, 5, 6]}, msg="goodbye", score=0.456)
