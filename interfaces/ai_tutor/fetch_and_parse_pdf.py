import os
import threading

import cv2
import wget
import json
import base64
import numpy as np
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path

import unify
from prompts import *

url = (
    "https://www.ocr.org.uk/Images/169000-foundation-tier-sample-assessment"
    "-materials.pdf"
)
this_dir = os.path.dirname(__file__)
pdfs_dir = os.path.join(this_dir, "pdfs")
os.makedirs(pdfs_dir, exist_ok=True)
fname = url.split("/")[-1]
pdf_path = os.path.join(pdfs_dir, fname)
if not os.path.exists(pdf_path):
    fname = wget.download(url, out=pdfs_dir)
pdf_path = os.path.join(pdfs_dir, fname)
pdf_dir = os.path.join(pdfs_dir, fname[:-4])
os.makedirs(pdf_dir, exist_ok=True)
reader = PdfReader(pdf_path)


def parse_pdf_into_papers_and_markschemes():
    paper_cover_text = (
        "completetheboxesabovewithyourname,centrenumberandcandidatenumber."
    )
    markscheme_cover_text = "markscheme"
    paper_cover_pages = list()
    markscheme_cover_pages = list()
    looking_for_paper = True

    for i, page in enumerate(reader.pages):
        text_stripped = page.extract_text().lower().replace(" ", "")
        if looking_for_paper and paper_cover_text in text_stripped:
            paper_cover_pages.append(i)
            looking_for_paper = False
        elif not looking_for_paper and markscheme_cover_text in text_stripped:
            markscheme_cover_pages.append(i)
            looking_for_paper = True

    left_pointer = paper_cover_pages.pop(0)
    count = 1
    while paper_cover_pages or markscheme_cover_pages:
        count_dir = os.path.join(pdf_dir, str(count))
        os.makedirs(count_dir, exist_ok=True)
        # paper
        writer = PdfWriter()
        right_pointer = markscheme_cover_pages.pop(0)
        [writer.add_page(pg) for pg in reader.pages[left_pointer:right_pointer]]
        paper_fpath = os.path.join(count_dir, "paper.pdf")
        writer.write(paper_fpath)
        left_pointer = right_pointer
        # mark-scheme
        writer = PdfWriter()
        if paper_cover_pages:
            right_pointer = paper_cover_pages.pop(0)
        else:
            right_pointer = len(reader.pages) + 1
        [writer.add_page(pg) for pg in reader.pages[left_pointer:right_pointer]]
        markscheme_fpath = os.path.join(count_dir, "markscheme.pdf")
        writer.write(markscheme_fpath)
        left_pointer = right_pointer
        # count
        count += 1


def _fill_missing_questions(questions_to_pages):
    prev_question_num = 0
    new_questions_to_pages = questions_to_pages.copy()
    for question_num, pages in questions_to_pages.items():
        if question_num != prev_question_num + 1:
            union_of_pages = list(
                dict.fromkeys(questions_to_pages[prev_question_num] + pages),
            )
            for q_num in range(prev_question_num + 1, question_num):
                new_questions_to_pages[q_num] = union_of_pages
        prev_question_num = question_num
    return dict(sorted(new_questions_to_pages.items()))


def parse_paper(paper_num):
    question_detector = unify.Unify(
        "o1@openai",
        cache=True,
        system_message=QUESTION_DETECTION,
    )
    question_parser = unify.Unify("o1@openai", cache=True)
    diagram_detector = unify.Unify("o1@openai", cache=True)
    text_only_detector = unify.Unify(
        "o1@openai",
        cache=True,
        system_message=TEXT_ONLY_DETECTION,
    )

    paper_dir = os.path.join(pdf_dir, str(paper_num), "paper")
    os.makedirs(paper_dir, exist_ok=True)
    paper_path = paper_dir + ".pdf"

    reader = PdfReader(paper_path)
    questions = dict()

    all_images = [
        np.asarray(img.getdata())
        .reshape(img.size[1], img.size[0], 3)
        .astype(
            np.uint8,
        )
        for img in convert_from_path(paper_path)
    ]

    diagram_images = dict()

    def encode_image(image_path):
        _, buffer = cv2.imencode(".jpg", image_path)
        return base64.b64encode(buffer).decode("utf-8")

    def parse_question_detector(response):
        parsed = (
            response.lower()
            .split(
                "answer:",
            )[-1]
            .replace(
                "\n",
                "",
            )
            .replace(
                "`",
                "",
            )
            .replace(
                " ",
                "",
            )
            .split(
                ",",
            )
        )
        return parsed

    def parse_into_pages():
        diagram_detector.set_system_message(DIAGRAM_DETECTION_ON_PAGE)
        question_to_pages = dict()
        latest_num = 0
        latest_char = "`"
        for page_num, page in enumerate(reader.pages):
            page_num += 1
            text = page.extract_text().split("OCR  2024  J560/0")[-1][2:]
            # detect diagrams on page
            img = all_images[page_num - 1]
            diagram_response = diagram_detector.generate(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": text,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,"
                                    f"{encode_image(img)}",
                                },
                            },
                        ],
                    },
                ],
            )
            contains_diagram = "yes" in diagram_response.split("\n")[-1].strip().lower()
            if contains_diagram:
                diagram_images[page_num] = img
                img_dir = os.path.join(paper_dir, "imgs")
                os.makedirs(img_dir, exist_ok=True)
                fname = f"page{page_num}.png"
                if not os.path.exists(fname):
                    cv2.imwrite(os.path.join(img_dir, fname), img)
            question_detector.set_system_message(
                QUESTION_DETECTION.replace(
                    "{n0}",
                    str(latest_num + 1),
                )
                .replace(
                    "{n1}",
                    str(latest_num + 2),
                )
                .replace(
                    "{n2}",
                    str(latest_num + 3),
                )
                .replace(
                    "{c0}",
                    chr(ord(latest_char) + 1),
                )
                .replace(
                    "{c1}",
                    chr(ord(latest_char) + 2),
                )
                .replace(
                    "{c2}",
                    chr(ord(latest_char) + 3),
                ),
            )
            response = question_detector.generate(text)
            detected_qs = parse_question_detector(response)
            if not all(
                v.isdigit() or (len(v) == 1 and v.isalpha()) for v in detected_qs
            ):
                continue
            previous_q_overflow = detected_qs[0].isalpha()
            if previous_q_overflow:
                question_to_pages[detected_numeric[-1]] += [page_num]
            detected_numeric = [int(v) for v in detected_qs if v.isnumeric()]
            if detected_numeric:
                latest_num = max(detected_numeric)
            last_question = detected_qs[-1]
            latest_char = "`" if last_question.isnumeric() else last_question
            for question in detected_numeric:
                question_to_pages[question] = [page_num]
        return _fill_missing_questions(question_to_pages), max(detected_numeric)

    question_to_pages, num_questions = parse_into_pages()

    json_file_lock = threading.Lock()

    def parse_question(question_num: int):
        pages = question_to_pages[question_num]
        current_text = "".join([reader.pages[pg - 1].extract_text() for pg in pages])
        question_parser.set_system_message(
            QUESTION_PARSER.replace(
                "{question_number}",
                str(question_num),
            )
            .replace(
                "{preceding}",
                str(question_num - 1),
            )
            .replace(
                "{subsequent}",
                str(question_num + 1),
            ),
        )
        question_parsed = question_parser.generate(current_text)
        response = text_only_detector.generate(question_parsed)
        text_only = "yes" in response.split("\n")[-1].lower()
        questions[question_num] = {"text": question_parsed, "text-only": text_only}
        parsed = json.dumps(dict(sorted(questions.items())), indent=4)
        json_file_lock.acquire()
        with open(os.path.join(paper_dir, "parsed.json"), "w+") as file:
            file.write(parsed)
        json_file_lock.release()

        # image
        imgs = [diagram_images[pg] for pg in pages if pg in diagram_images]
        if not imgs:
            return
        diagram_detector.set_system_message(
            DIAGRAM_DETECTION_IN_QUESTION.replace(
                "{question_number}",
                str(question_num),
            )
            .replace(
                "{preceding}",
                str(question_num - 1),
            )
            .replace(
                "{subsequent}",
                str(question_num + 1),
            ),
        )
        diagram_response = diagram_detector.generate(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": current_text,
                        },
                    ]
                    + [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encode_image(img)}",
                            },
                        }
                        for img in imgs
                    ],
                },
            ],
        )
        contains_diagram = "yes" in diagram_response.split("\n")[-1].strip().lower()
        # incrementally save to file
        if not contains_diagram:
            return
        img_dir = os.path.join(paper_dir, "imgs")
        os.makedirs(img_dir, exist_ok=True)
        fnames = [f"page{pg}.png" for pg in pages if pg in diagram_images]
        questions[question_num]["images"] = fnames
        for fname, img in zip(fnames, imgs):
            if not os.path.exists(fname):
                cv2.imwrite(os.path.join(img_dir, fname), img)

    unify.map(parse_question, list(range(1, num_questions + 1)))


def parse_markscheme(paper_num):
    question_detector = unify.Unify(
        "o1@openai",
        cache=True,
        system_message=QUESTION_ANSWER_DETECTION,
    )
    question_answer_parser = unify.Unify("o1@openai", cache=True)
    diagram_detector = unify.Unify("o1@openai", cache=True)
    num_marks_detector = unify.Unify(
        "o1@openai",
        cache=True,
        system_message=NUM_MARKS_DETECTION,
    )

    markscheme_dir = os.path.join(pdf_dir, str(paper_num), "markscheme")
    os.makedirs(markscheme_dir, exist_ok=True)
    markscheme_path = markscheme_dir + ".pdf"

    reader = PdfReader(markscheme_path)
    questions = dict()

    all_images = [
        np.asarray(img.getdata())
        .reshape(img.size[1], img.size[0], 3)
        .astype(
            np.uint8,
        )
        for img in convert_from_path(markscheme_path)
    ]

    diagram_images = dict()

    def encode_image(image_path):
        _, buffer = cv2.imencode(".jpg", image_path)
        return base64.b64encode(buffer).decode("utf-8")

    def parse_question_detector(response):
        parsed = (
            response.lower()
            .split(
                "answer:",
            )[-1]
            .replace(
                "\n",
                "",
            )
            .replace(
                "`",
                "",
            )
            .replace(
                " ",
                "",
            )
            .split(
                ",",
            )
        )
        return parsed

    def parse_into_pages():
        diagram_detector.set_system_message(
            DIAGRAM_DETECTION_ON_PAGE.replace("questions", "questions or answers"),
        )
        question_to_pages = dict()
        latest_num = 0
        latest_char = "`"
        for page_num, page in enumerate(reader.pages):
            page_num += 1
            text = page.extract_text().split("OCR  2024  J560/0")[-1][2:]
            # detect diagrams on page
            img = all_images[page_num - 1]
            diagram_response = diagram_detector.generate(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": text,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,"
                                    f"{encode_image(img)}",
                                },
                            },
                        ],
                    },
                ],
            )
            contains_diagram = "yes" in diagram_response.split("\n")[-1].strip().lower()
            if contains_diagram:
                diagram_images[page_num] = img
                img_dir = os.path.join(markscheme_dir, "imgs")
                os.makedirs(img_dir, exist_ok=True)
                fname = f"page{page_num}.png"
                if not os.path.exists(fname):
                    cv2.imwrite(os.path.join(img_dir, fname), img)
            question_detector.set_system_message(
                QUESTION_ANSWER_DETECTION.replace(
                    "{n0}",
                    str(latest_num + 1),
                )
                .replace(
                    "{n1}",
                    str(latest_num + 2),
                )
                .replace(
                    "{n2}",
                    str(latest_num + 3),
                )
                .replace(
                    "{c0}",
                    chr(ord(latest_char) + 1),
                )
                .replace(
                    "{c1}",
                    chr(ord(latest_char) + 2),
                )
                .replace(
                    "{c2}",
                    chr(ord(latest_char) + 3),
                ),
            )
            response = question_detector.generate(text)
            detected_qs = parse_question_detector(response)
            if not all(
                v.isdigit() or (len(v) == 1 and v.isalpha()) for v in detected_qs
            ):
                continue
            previous_q_overflow = detected_qs[0].isalpha()
            if previous_q_overflow:
                question_to_pages[detected_numeric[-1]] += [page_num]
            detected_numeric = [int(v) for v in detected_qs if v.isnumeric()]
            if detected_numeric:
                latest_num = max(detected_numeric)
            last_question = detected_qs[-1]
            latest_char = "`" if last_question.isnumeric() else last_question
            for question in detected_numeric:
                question_to_pages[question] = [page_num]
        return _fill_missing_questions(question_to_pages), max(detected_numeric)

    question_to_pages, num_questions = parse_into_pages()

    for question_num in range(1, num_questions + 1):
        pages = question_to_pages[question_num]
        current_text = "".join([reader.pages[pg - 1].extract_text() for pg in pages])
        question_answer_parser.set_system_message(
            QUESTION_ANSWER_PARSER.replace(
                "{question_number}",
                str(question_num),
            )
            .replace(
                "{preceding}",
                str(question_num - 1),
            )
            .replace(
                "{subsequent}",
                str(question_num + 1),
            ),
        )
        qna = question_answer_parser.generate(current_text)
        response = num_marks_detector.generate(qna)
        num_marks = int(
            "".join([c for c in response.split("\n")[-1].lower() if c.isdigit()]),
        )
        questions[question_num] = {"text": qna, "num-marks": num_marks}
        parsed = json.dumps(questions, indent=4)
        with open(os.path.join(markscheme_dir, "parsed.json"), "w+") as file:
            file.write(parsed)

        # image
        imgs = [diagram_images[pg] for pg in pages if pg in diagram_images]
        if not imgs:
            continue
        diagram_detector.set_system_message(
            DIAGRAM_DETECTION_IN_QUESTION.replace(
                "{question_number}",
                str(question_num),
            )
            .replace(
                "{preceding}",
                str(question_num - 1),
            )
            .replace(
                "{subsequent}",
                str(question_num + 1),
            ),
        )
        diagram_response = diagram_detector.generate(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": current_text,
                        },
                    ]
                    + [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encode_image(img)}",
                            },
                        }
                        for img in imgs
                    ],
                },
            ],
        )
        contains_diagram = "yes" in diagram_response.split("\n")[-1].strip().lower()
        # incrementally save to file
        if not contains_diagram:
            continue
        img_dir = os.path.join(markscheme_dir, "imgs")
        os.makedirs(img_dir, exist_ok=True)
        fnames = [f"page{pg}.png" for pg in pages if pg in diagram_images]
        questions[question_num]["images"] = fnames
        for fname, img in zip(fnames, imgs):
            if not os.path.exists(fname):
                cv2.imwrite(os.path.join(img_dir, fname), img)


if __name__ == "__main__":
    parse_pdf_into_papers_and_markschemes()
    subdirs = sorted(os.listdir(pdf_dir))

    def _parse_paper(subdir: str):
        target_paper_fpath = os.path.join(pdf_dir, subdir, "paper/parsed.json")
        if not os.path.exists(target_paper_fpath):
            parse_paper(int(subdir))

    unify.map(_parse_paper, subdirs)

    def _parse_markscheme(subdir: str):
        target_markscheme_fpath = os.path.join(
            pdf_dir,
            subdir,
            "markscheme/parsed.json",
        )
        if not os.path.exists(target_markscheme_fpath):
            parse_markscheme(int(subdir))

    unify.map(_parse_markscheme, subdirs)
