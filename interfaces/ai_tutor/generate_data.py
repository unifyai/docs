import os
import json
import cv2
import argparse
from pydantic import BaseModel

import unify
unify.CLIENT_LOGGING = True
from prompts import *
from helpers import load_questions_and_answers, encode_image


parser = argparse.ArgumentParser()
parser.add_argument('--labelled', help='Generate synthetic labelled data',
                    action="store_true")
parser.add_argument('--usage', help='Generate synthetic usage data',
                    action="store_true")
args = parser.parse_args()
mode = "usage" if args.usage else "labelled"

this_dir = os.path.dirname(__file__)
pdfs_dir = os.path.join(this_dir, "pdfs")


class Response(BaseModel):
    rationale: str
    answer: str


def generate_question(question, data, idx):
    subject_dir = os.path.join(pdfs_dir, data["subject"].replace(" ", "_"))
    paper_dir = os.path.join(subject_dir, data["paper_id"].replace(" ", "_"))
    paper_imgs_dir = os.path.join(paper_dir, "paper/imgs")
    assert os.path.exists(paper_imgs_dir)
    img_fpaths = [
        os.path.join(paper_imgs_dir, f"page{pg}.png") for pg in data["question_pages"]
    ]
    imgs = [cv2.imread(fpath, -1) for fpath in img_fpaths]
    to_write = dict()
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    fname = f"{mode}_data_{idx}"
    data_path = os.path.join(data_dir, fname)
    generation_client = unify.Unify("o1@openai", response_format=Response, cache=True)
    targets = dict()
    for target in range(data["marks"] + 1):
        generation_client.set_system_message(
            GENERATE_RESPONSE_PROMPT.replace(
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
                json.dumps(data["answer"], indent=4),
            )
        )
        response = generation_client.generate(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,"
                                       f"{encode_image(img)}",
                            },
                        }
                    for img in imgs],
                },
            ],
        )
        targets[target] = json.loads(response)
    targets["subject"] = data["subject"]
    targets["paper_id"] = data["paper_id"]
    targets["question_num"] = int(data["question_num"])
    targets["markscheme"] = data["answer"]
    targets["available_marks"] = int(data["marks"])
    targets["question_pages"] = [int(pg) for pg in data["question_pages"]]
    targets["markscheme_pages"] = [int(pg) for pg in data["markscheme_pages"]]
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
    args = [
        (question, dct, i) for i, (question, dct) in enumerate(qna.items())
        if dct["correctly_parsed"]
    ]
    unify.map(generate_question, args)
    combine_data()


if __name__ == "__main__":
    os.makedirs(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "data"),
        exist_ok=True
    )
    assert not (args.labelled and args.usage), \
        "Please specify either --labelled or --usage, not both."
    assert args.labelled or args.usage, \
        "Please specify one of --labelled or --usage."
    main()
