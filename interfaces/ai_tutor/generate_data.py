import os
import json
import unify
import argparse
from prompts import *
from helpers import load_questions_and_answers


parser = argparse.ArgumentParser()
parser.add_argument('--labelled', help='Generate synthetic labelled data',
                    action="store_true")
parser.add_argument('--usage', help='Generate synthetic usage data',
                    action="store_true")
args = parser.parse_args()
mode = "usage" if args.usage else "labelled"


def generate_question(
        question, markscheme, available_marks, subject, paper_id, question_num,
        question_imgs, markscheme_imgs, idx
):
    data = dict()
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    fname = f"{mode}_data_{idx}"
    data_path = os.path.join(data_dir, fname)
    generation_client = unify.Unify("o1@openai", cache=True)
    targets = dict()
    for target in range(available_marks + 1):
        response = generation_client.generate(
            system_message=GENERATE_RESPONSE_PROMPT.replace(
                "{target}",
                str(target),
            )
            .replace(
                "{num_marks}",
                str(available_marks),
            )
            .replace(
                "{question}",
                question,
            )
            .replace(
                "{markscheme}",
                markscheme,
            ),
        )
        targets[target] = [ans for ans in response.split("Answer:")[1:]]
    targets["subject"] = subject
    targets["paper_id"] = paper_id
    targets["question_num"] = question_num
    targets["markscheme"] = markscheme
    targets["available_marks"] = available_marks
    targets["question_imgs"] = question_imgs
    targets["markscheme_imgs"] = markscheme_imgs
    # incremental file writing
    data[question] = targets
    with open(data_path, "w+") as f:
        f.write(json.dumps(data, indent=4))


def combine_data():
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    if os.path.exists(os.path.join(data_dir, f"{mode}_data.json")):
        os.remove(os.path.join(data_dir, f"{mode}_data.json"))
    data_paths = [
        os.path.join(data_dir, fname) for fname in os.listdir(data_dir)
        if fname.startswith(f"{mode}_data_")
    ]
    data = {}
    for data_path in data_paths:
        with open(data_path, "r") as f:
            this_data = json.load(f)
        data = {**data, **this_data}
        os.remove(data_path)
    with open(os.path.join(data_dir, f"{mode}_data.json"), "w+") as f:
        f.write(json.dumps(data, indent=4))


def main():
    qna = load_questions_and_answers()
    questions = list(qna.keys())
    ans_n_marks = list(qna.values())
    num_questions = len(questions)
    assert num_questions == len(ans_n_marks)
    markschemes = [dct["answer"] for dct in ans_n_marks]
    available_marks = [dct["marks"] for dct in ans_n_marks]
    subjects = [dct["subject"] for dct in ans_n_marks]
    paper_ids = [dct["paper_id"] for dct in ans_n_marks]
    question_nums = [dct["question_num"] for dct in ans_n_marks]
    question_imgs = [
        [fp.split("/")[-1] for fp in dct["question_imgs"]]
        if dct["question_imgs"] else None
        for dct in ans_n_marks
    ]
    markscheme_imgs = [
        [fp.split("/")[-1] for fp in dct["markscheme_imgs"]]
        if dct["markscheme_imgs"] else None
        for dct in ans_n_marks
    ]
    idxs = range(num_questions)
    unify.map(
        generate_question, questions, markschemes, available_marks, subjects, paper_ids,
        question_nums, question_imgs, markscheme_imgs, idxs
    )
    combine_data()


if __name__ == "__main__":
    assert not (args.labelled and args.usage), \
        "Please specify either --labelled or --usage, not both."
    assert args.labelled or args.usage, \
        "Please specify one of --labelled or --usage."
    main()
