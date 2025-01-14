import os
import csv
import json
import random

import unify
from helpers import load_questions_and_answers, encode_image


def load_data():
    this_dir = os.path.dirname(os.path.realpath(__file__))
    student_info_path = os.path.join(this_dir, "student_info.csv")
    with open(student_info_path, "r") as f:
        reader = csv.reader(f)
        student_data = list(reader)[1:]
    data_dir = os.path.join(this_dir, "data")
    data_paths = [os.path.join(data_dir, fname) for fname in os.listdir(data_dir)]
    data = dict()
    for data_path in data_paths:
        with open(data_path, "r") as f:
            data = {**data, **json.load(f)}
    return data, student_data


def main():
    data, student_data = load_data()
    qna = load_questions_and_answers()
    questions = list(data.keys())
    with unify.Context("QnATraffic"):
        while True:
            first, last, email = random.choice(student_data)
            question = random.choice(questions)
            provided_answers = random.choice(list(data[question].values()))
            provided_answer = random.choice(provided_answers)
            qna_dct = qna[question]
            question_imgs = qna_dct.get("question_imgs")
            if question_imgs:
                question_imgs = [encode_image(fpath) for fpath in question_imgs]
            markscheme_imgs = qna_dct.get("markscheme_imgs")
            if markscheme_imgs:
                markscheme_imgs = [encode_image(fpath) for fpath in markscheme_imgs]
            unify.log(
                first_name=first,
                last_name=last,
                email=email,
                subject=None,
                paper_id=None,
                question_num=None,
                question=question,
                question_imgs=question_imgs[0] if question_imgs else None,
                provided_answer=provided_answer,
                markscheme=qna_dct.get("answer"),
                markscheme_imgs=markscheme_imgs[0] if markscheme_imgs else None,
                available_marks=qna_dct.get("marks"),
            )


if __name__ == "__main__":
    with unify.Project("EdTech", overwrite=True):
        main()
