import os
import csv
import json
import random

import unify


def load_data():
    this_dir = os.path.dirname(os.path.realpath(__file__))
    student_info_path = os.path.join(this_dir, "student_info.csv")
    with open(student_info_path, "r") as f:
        reader = csv.reader(f)
        student_data = list(reader)[1:]
    data_path = os.path.join(this_dir, "data")
    with open(data_path, "r") as f:
        data = json.load(f)
    return data, student_data


def main():
    data, student_data = load_data()
    questions = list(data.keys())
    with unify.Context("QnATraffic"):
        while True:
            first, last, email = random.choice(student_data)
            question = random.choice(questions)
            provided_answers = random.choice(list(data[question].values()))
            provided_answer = random.choice(provided_answers)
            unify.log(
                first_name=first,
                last_name=last,
                email=email,
                question=question,
                provided_answer=provided_answer
            )


if __name__ == "__main__":
    with unify.Project("EdTech", overwrite=True):
        main()
