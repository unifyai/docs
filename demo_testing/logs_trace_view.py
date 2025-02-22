import unify
unify.activate("nested-traced-view-demo")

@unify.traced
def inner_fn(a, b):
    return a + b

@unify.traced
def mid_fn(a, b):
    c = inner_fn(a, b)
    d = inner_fn(c, b)
    return c * d

@unify.traced
def outer_fn(a, b):
    c = mid_fn(a, b)
    d = mid_fn(c, a)
    return d / c

outer_fn(3, 4)
