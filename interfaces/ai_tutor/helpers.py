import os
import cv2
import json
import base64


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
                if not question.get("text-only"):
                    continue
                ans_n_marks = markscheme[question_num]
                answer, marks = ans_n_marks.get("text"), ans_n_marks.get("num-marks")
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
                questions_and_answers[question["text"]] = {
                    "subject": subject,
                    "paper_id": paper_id,
                    "question_num": question_num,
                    "pages": question["pages"],
                    "answer": answer,
                    "marks": marks,
                    "question_imgs": question_imgs,
                    "markscheme_imgs": markscheme_imgs,
                    "correctly_parsed": correctly_parsed,
                }
        return questions_and_answers
