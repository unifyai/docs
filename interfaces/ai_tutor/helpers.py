import os
import cv2
import json
import base64
from pydantic import create_model

VALID_NUMERALS = ("i", "ii", "iii", "iv", "v", "vi")


def build_response_format(question_num, sub_questions, dtype=str):
    response_keys = sub_questions if sub_questions else [str(question_num)]
    response_fields = dict(zip(response_keys, [(dtype, ...)] * len(response_keys)))
    return create_model('Response', **response_fields)


def is_invalid_question_order(detected_qs, valid_num, valid_char):
    valid_numeral = 0
    for i, item in enumerate(detected_qs):
        if item in VALID_NUMERALS:
            if item != VALID_NUMERALS[valid_numeral]:
                return True
            valid_numeral += 1
        elif item.isalpha():
            if item != valid_char:
                return True
            valid_char = chr(ord(valid_char) + 1)
            valid_numeral = 0
        elif item.isdigit():
            if item != valid_num:
                return True
            valid_num = str(int(valid_num) + 1)
            valid_char = "a"
            valid_numeral = 0
        else:
            raise ValueError(f"Invalid type for question: {item}")
    return False


def parse_key(k: str):
    """
    Splits the string on the first dot.
    - The part before the dot is turned into an integer (if there's no dot, the whole key is an integer).
    - The remainder (if any) is kept as a suffix for secondary sorting.
    """
    parts = k.split('.', 1)
    num = int(parts[0])                # integer portion
    suffix = parts[1] if len(parts) > 1 else ""  # suffix after the first dot, if any
    return num, suffix


def encode_image(image_path):
    _, buffer = cv2.imencode(".jpg", image_path)
    return base64.b64encode(buffer).decode("utf-8")


def load_questions_and_answers():
    questions_and_answers = dict()
    pdfs_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pdfs")
    for subject_dir in os.listdir(pdfs_dir):
        if subject_dir.endswith(".pdf"):
            continue
        subject = subject_dir.replace("_", " ")
        subject_dir_abs = os.path.join(pdfs_dir, subject_dir)
        for paper_dir in os.listdir(subject_dir_abs):
            if paper_dir.endswith(".pdf"):
                continue
            paper_id = paper_dir.replace("_", " ")
            paper_dir_abs = os.path.join(subject_dir_abs, paper_dir)
            with open(os.path.join(paper_dir_abs, "markscheme/parsed.json")) as f:
                markscheme = json.load(f)
            with open(os.path.join(paper_dir_abs, "paper/parsed.json")) as f:
                questions = json.load(f)
            for question_num, question in questions.items():
                if not question["text-only"]:
                    continue
                ans_n_marks = markscheme[question_num]
                markscheme_components, mark_breakdown = (
                    ans_n_marks["markscheme-components"], ans_n_marks["mark-breakdown"]
                )
                question_imgs = question.get("images")
                if question_imgs:
                    question_imgs = [
                        os.path.join(
                            os.path.join(paper_dir_abs, "paper/imgs"),
                            fname,
                        )
                        for fname in question_imgs
                    ]
                markscheme_imgs = ans_n_marks.get("images")
                if markscheme_imgs:
                    markscheme_imgs = [
                        os.path.join(
                            os.path.join(paper_dir_abs, "markscheme/imgs"),
                            fname,
                        )
                        for fname in markscheme_imgs
                    ]
                correctly_parsed = (question["correctly_parsed"] and
                                    ans_n_marks["correctly_parsed"])
                questions_and_answers[question["question"]] = {
                    "subject": subject,
                    "paper_id": paper_id,
                    "question_num": question_num,
                    "question_pages": question["pages"],
                    "markscheme_pages": ans_n_marks["pages"],
                    "answer": markscheme_components,
                    "marks": mark_breakdown,
                    "question_imgs": question_imgs,
                    "markscheme_imgs": markscheme_imgs,
                    "correctly_parsed": correctly_parsed,
                }
        return questions_and_answers
