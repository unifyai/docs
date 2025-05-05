import unify

unify.activate("histogram-demo", overwrite=True)
import random
from datetime import date

n = 10
for month in range(1, 13):
    num_queries = random.randint(month * n, (month + 10) * n)
    print(f"creating logs for {month} with {num_queries} queries... ")
    unify.create_logs(
        entries=[
            {"date": date(2025, month, random.randint(1, 28)).isoformat()}
            for _ in range(num_queries)
        ]
    )
    print(f"created {num_queries} logs for {month}")
