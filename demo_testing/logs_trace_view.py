import unify
unify.activate("traced-view-demo")

@unify.traced
def my_function(a, b):
    return a + b

my_function(1, 2)
