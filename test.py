import unify
dataset1 = unify.Dataset(["a", "b", "c"])
dataset2 = unify.Dataset(["a", "b"])
assert dataset2 in dataset1
assert "a" in dataset1
assert unify.Prompt("b") in dataset1
assert ["b", "c"] in dataset1
assert "d" not in dataset1
dataset3 = unify.Dataset(["c", "d"])
assert dataset3 not in dataset1