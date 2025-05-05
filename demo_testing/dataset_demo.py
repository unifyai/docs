import unify

unify.activate("dataset-demo", overwrite=True)
import random

my_dataset = unify.Dataset(
    [item * 100 for item in list(range(100))], name="my_dataset"
).sync()
random.seed(0)
my_sub_dataset = unify.Dataset(
    [d * 100 for d in random.sample(list(range(100)), 10)], name="my_sub_dataset"
).sync()
