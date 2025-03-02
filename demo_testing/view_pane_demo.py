import unify
import random
from datetime import datetime, timedelta
unify.activate("view-pane-demo", overwrite=True)


num_employees = 20
ages = [
    random.randint(20, 50)
    for _ in range(num_employees)
]
catchphrases = random.choices(
    [
        "hello... friend",
        "hell no",
        "did you ask o3?",
        "will do it tomorrow",
        "ask the intern",
    ],
    k=num_employees,
)
last_logins = [
    (datetime.now() - timedelta(
        days=random.randint(0, 5)
    )).isoformat()
    for _ in range(num_employees)
]
open_task_progress = [
    {
        task: random.random()
        for task in random.sample(
            [
                "add NextJS loader",
                "SQL migration",
                "refactor life",
            ],
            random.randint(0, 3),
        )
    }
    for _ in range(num_employees)
]

for age, catchphrase, last_login, otp in zip(
    ages, catchphrases, last_logins, open_task_progress
):
    unify.log(
        age=age,
        catchphrase=catchphrase,
        how_10x=random.random()*10,
        last_login=last_login,
        open_task_progress=otp,
        will_to_live=random.choice([True, False]),
    )
