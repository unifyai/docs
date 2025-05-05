import unify

unify.activate("gender_loc_salary", overwrite=True)
import random

gender_factors = {"male": 1500, "female": 750}
loc_offsets = {"UK": 15000, "US": 45000}
for gender in ["male", "female"]:
    for loc in ["UK", "US"]:
        for age in range(20, 55):
            unify.log(
                gender=gender,
                nationality=loc,
                age=age,
                salary=(
                    age * 500
                    + age * gender_factors[gender] * random.random()
                    + loc_offsets[loc] * random.random()
                ),
            )
