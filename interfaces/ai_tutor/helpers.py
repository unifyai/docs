import os
import cv2
import json
import base64


def load_questions_and_answers():
    questions_and_answers = dict()
    pdfs_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pdfs")
    for papers_dir in os.listdir(pdfs_dir):
        if papers_dir.endswith(".pdf"):
            continue
        papers_dir_abs = os.path.join(pdfs_dir, papers_dir)
        for paper_dir in os.listdir(papers_dir_abs):
            paper_dir_abs = os.path.join(papers_dir_abs, paper_dir)
            with open(os.path.join(paper_dir_abs, 'markscheme/parsed.json')) as f:
                markscheme = json.load(f)
            with open(os.path.join(paper_dir_abs, 'paper/parsed.json')) as f:
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
                            os.path.join(paper_dir_abs, 'paper/imgs'), fname
                        )
                        for fname in question_imgs
                    ]
                markscheme_imgs = ans_n_marks.get("images")
                if markscheme_imgs:
                    markscheme_imgs = [
                        os.path.join(
                            os.path.join(paper_dir_abs, 'markscheme/imgs'), fname
                        )
                        for fname in markscheme_imgs
                    ]
                questions_and_answers[question.get("text")] = {
                    "answer": answer,
                    "marks": marks,
                    "question_imgs": question_imgs,
                    "markscheme_imgs": markscheme_imgs
                }
    return questions_and_answers


def encode_image(image_path):
    success, buffer = cv2.imencode(".png", cv2.imread(image_path))
    assert success
    return base64.b64encode(buffer).decode("utf-8")
