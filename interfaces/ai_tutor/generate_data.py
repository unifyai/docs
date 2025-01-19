import os
import json
import unify
import argparse
from pydantic import BaseModel

from prompts import *
from helpers import load_questions_and_answers


parser = argparse.ArgumentParser()
parser.add_argument('--labelled', help='Generate synthetic labelled data',
                    action="store_true")
parser.add_argument('--usage', help='Generate synthetic usage data',
                    action="store_true")
args = parser.parse_args()
mode = "usage" if args.usage else "labelled"


class Response(BaseModel):
    rationale: str
    answer: str


def generate_question(question, data, idx):
    to_write = dict()
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    fname = f"{mode}_data_{idx}"
    data_path = os.path.join(data_dir, fname)
    generation_client = unify.Unify("o1@openai", cache=True)
    targets = dict()
    for target in range(data["marks"] + 1):
        response = generation_client.generate(
            system_message=GENERATE_RESPONSE_PROMPT.replace(
                "{target}",
                str(target),
            )
            .replace(
                "{num_marks}",
                str(data["marks"]),
            )
            .replace(
                "{question}",
                question,
            ).replace(
                "{question_num}",
                str(data["question_num"])
            )
            .replace(
                "{markscheme}",
                data["answer"],
            ),
            response_format=Response,
        )
        targets[target] = json.loads(response)
    targets["subject"] = data["subject"]
    targets["paper_id"] = data["paper_id"]
    targets["question_num"] = data["question_num"]
    targets["markscheme"] = data["answer"]
    targets["available_marks"] = data["marks"]
    if data["question_imgs"]:
        targets["question_imgs"] = [fp.split("/")[-1] for fp in data["question_imgs"]]
    else:
        targets["question_imgs"] = None
    if data["markscheme_imgs"]:
        targets["markscheme_imgs"] = [fp.split("/")[-1] for fp in data["markscheme_imgs"]]
    else:
        targets["markscheme_imgs"] = None
    # incremental file writing
    to_write[question] = targets
    with open(data_path, "w+") as f:
        f.write(json.dumps(to_write, indent=4))


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
    args = [(question, dct, i) for i, (question, dct) in enumerate(qna.items())]
    unify.map(generate_question, args)
    combine_data()


if __name__ == "__main__":
    assert not (args.labelled and args.usage), \
        "Please specify either --labelled or --usage, not both."
    assert args.labelled or args.usage, \
        "Please specify one of --labelled or --usage."
    main()
