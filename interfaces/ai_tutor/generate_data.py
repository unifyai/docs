import os
import json
import unify
from prompts import *
from helpers import load_questions_and_answers


def generate_question(question, answer, marks, idx):
    data = dict()
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"data_{idx}")
    generation_client = unify.Unify("o1@openai", cache=True)
    targets = dict()
    for target in range(marks + 1):
        response = generation_client.generate(
            system_message=GENERATE_RESPONSE_PROMPT.replace(
                "{target}",
                str(target),
            )
            .replace(
                "{num_marks}",
                str(marks),
            )
            .replace(
                "{question}",
                question,
            )
            .replace(
                "{answer}",
                answer,
            ),
        )
        targets[target] = [ans for ans in response.split("Answer:")[1:]]
    data[question] = targets
    # incremental file writing
    with open(data_path, "w+") as f:
        f.write(json.dumps(data, indent=4))


def combine_data():
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    data_paths = [os.path.join(data_dir, fname) for fname in os.listdir(data_dir)]
    data = {}
    for data_path in data_paths:
        with open(data_path, "r") as f:
            this_data = json.load(f)
        data = {**data, **this_data}
    with open(os.path.join(data_dir, "data.json"), "w+") as f:
        f.write(json.dumps(data, indent=4))


def main():
    qna = load_questions_and_answers()
    questions = list(qna.keys())
    ans_n_marks = list(qna.values())
    num_questions = len(questions)
    assert num_questions == len(ans_n_marks)
    answers = [dct["answer"] for dct in ans_n_marks]
    marks = [dct["marks"] for dct in ans_n_marks]
    idxs = range(num_questions)
    unify.map(generate_question, questions, answers, marks, idxs)
    combine_data()


if __name__ == "__main__":
    main()
