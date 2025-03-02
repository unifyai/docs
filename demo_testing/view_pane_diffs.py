import unify
from datetime import datetime
unify.activate("view-pane-diffs", overwrite=True)

unify.log(
    x=1,
    y=1.2,
    msg="hello friend",
    flag=True,
    appointment=datetime(2025, 3, 23, 10, 30).isoformat(),
    dct={"a": 1, "b": 2},
    lst=[1, 2, 3],
)
unify.log(
    x=2,
    y=1.2,
    msg="hey buddy",
    flag=True,
    appointment=datetime(2025, 2, 15, 11, 30).isoformat(),
    dct={"b": 2, "c": 3},
    lst=[4, 5, 6],
)
unify.log(
    x=3,
    y=1.3,
    msg="hello partner",
    flag=False,
    appointment=datetime(2025, 4, 11, 12, 30).isoformat(),
    dct={"a": 1, "b": 3, "c": 4},
    lst=[1, 2, 3, 4],
)
