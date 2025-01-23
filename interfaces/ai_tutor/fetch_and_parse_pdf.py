import os
import cv2
import wget
import json
import threading
import numpy as np
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path

import unify
from prompts import *
from helpers import encode_image, parse_key

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


def prune_page_number(pg_text: str, page_num: int, question_num: int):
    if page_num == question_num:
        return pg_text
    # remove page number to avoid any confusion with question number
    split = pg_text.split(str(question_num))
    if len(split) == 1:
        return pg_text
    pre_q = split[0]
    post_q = split[1:]
    pre_q = pre_q.replace(str(page_num), "")
    return str(question_num).join([pre_q] + post_q)


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


def _fill_missing_questions_n_pages(questions_to_pages):
    prev_question_num = 0
    prev_pages = list()
    new_questions_to_pages = questions_to_pages.copy()
    all_alphanum = list(questions_to_pages.keys())
    all_pages = list(questions_to_pages.values())
    for i, (question_alphanum, pages) in enumerate(questions_to_pages.items()):
        question_num = int(question_alphanum.split(".")[0])
        if question_num not in (prev_question_num, prev_question_num + 1):
            min_pg = min(all_pages[i-1])
            max_pg = max(pages)
            union_of_pages = list(range(min_pg, max_pg + 1))
            for q_num in range(prev_question_num + 1, question_num):
                # we somehow missed the entire question, let's assume there are no
                # sub-question components (a, b, c etc.)
                new_questions_to_pages[str(q_num)] = union_of_pages
        elif prev_pages and pages[0] > prev_pages[-1] + 1:
            prev_alphanum = all_alphanum[i-1]
            new_questions_to_pages[prev_alphanum] = (
                list(range(prev_pages[0], pages[0] + 1))
            )
            new_questions_to_pages[question_alphanum] = (
                list(range(prev_pages[-1], pages[-1] + 1))
            )
        prev_question_num = question_num
        prev_pages = pages
    return dict(sorted(new_questions_to_pages.items()))


def parse_paper(paper_num):
    question_detector = unify.Unify(
        "o1@openai",
        cache=True,
        system_message=QUESTION_DETECTION,
    )
    diagram_detector = unify.Unify("o1@openai", cache=True)

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
            text = prune_page_number(text, page_num, latest_num+1)
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
            img_dir = os.path.join(paper_dir, "imgs")
            os.makedirs(img_dir, exist_ok=True)
            fname = f"page{page_num}.png"
            if not os.path.exists(fname):
                cv2.imwrite(os.path.join(img_dir, fname), img)
            if contains_diagram:
                diagram_images[page_num] = img
            question_detector.set_system_message(
                QUESTION_DETECTION.replace(
                    "{n-1}",
                    str(latest_num),
                ).replace(
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
                ).replace(
                    "{explanation}",
                    f"did not have any alpha sub-questions, so we should see a "
                    f"numeric question first on this page, possibly followed by `a`" if
                    latest_char == "`" else f"ended with question {latest_num} {latest_char}"
                ),
            )
            response = question_detector.generate(
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
            detected_qs = parse_question_detector(response)
            if not all(
                v.isdigit() or (len(v) == 1 and v.isalpha()) for v in detected_qs
            ):
                continue
            num = latest_num
            for i, item in enumerate(detected_qs):
                if item.isalpha():
                    question_to_pages[f"{num}.{item}"] = [page_num]
                elif item.isdigit():
                    if len(detected_qs) == i+1 or detected_qs[i+1].isdigit():
                        question_to_pages[item] = [page_num]
                    num = int(item)
                else:
                    raise ValueError(f"Invalid type for question: {item}")
            latest_num = num
            latest_char = "`" if detected_qs[-1].isnumeric() else detected_qs[-1]
        return _fill_missing_questions_n_pages(question_to_pages), latest_num

    question_to_pages, num_questions = parse_into_pages()
    question_to_pages = dict(
        sorted(question_to_pages.items(), key=lambda item: parse_key(item[0]))
    )
    with open(os.path.join(paper_dir, "question_to_pages.json"), "w+") as file:
        file.write(json.dumps(question_to_pages, indent=4))

    json_file_lock = threading.Lock()

    def parse_question(question_num: int):
        question_parser = unify.Unify("o1@openai", cache=True)
        text_only_detector = unify.Unify(
            "o1@openai",
            cache=True,
            system_message=TEXT_ONLY_DETECTION,
        )
        sub_questions = [
            k.split(".")[-1] for k, v in question_to_pages.items()
            if k.startswith(str(question_num) + ".")
        ]
        pages = [
            v for k, v in question_to_pages.items()
            if (k == str(question_num) or k.startswith(str(question_num) + "."))
        ]
        pages = list(dict.fromkeys([item for sublist in pages for item in sublist]))
        current_text = "".join([reader.pages[pg - 1].extract_text() for pg in pages])
        imgs = [all_images[pg - 1] for pg in pages]
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
        question_parsed = question_parser.generate(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": current_text,
                        }
                    ] + [
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
        response = text_only_detector.generate(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": question_parsed,
                            }
                        ] + [
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
        text_only = "yes" in response.split("\n")[-1].lower()
        questions[question_num] = {
            "text": question_parsed,
            "text-only": text_only,
            "pages": pages,
            "sub-questions": sub_questions,
            "correctly_parsed": True,
        }
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


def parse_markscheme(paper_num, question_to_subquestions, subquestions):
    question_detector = unify.Unify(
        "o1@openai",
        cache=True,
        system_message=QUESTION_ANSWER_DETECTION,
    )
    diagram_detector = unify.Unify("o1@openai", cache=True)

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
        # remove accidental page numbers
        result = list()
        for item in reversed(parsed):
            if item.isdigit() and item in result:
                continue
            result.append(item)
        result.reverse()
        return result

    def parse_into_pages():
        diagram_detector.set_system_message(
            DIAGRAM_DETECTION_ON_PAGE.replace("questions", "questions or answers"),
        )
        question_to_pages = dict()
        latest_num = 0
        all_detected_qs = list()
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
            img_dir = os.path.join(markscheme_dir, "imgs")
            os.makedirs(img_dir, exist_ok=True)
            fname = f"page{page_num}.png"
            if not os.path.exists(fname):
                cv2.imwrite(os.path.join(img_dir, fname), img)
            if contains_diagram:
                diagram_images[page_num] = img
            question_detector.set_system_message(
                QUESTION_ANSWER_DETECTION.replace(
                    "{detected_so_far}",
                    "the full set of questions detected so far up to and including "
                    f"the last page are: {all_detected_qs}" if all_detected_qs else
                    "this is the first page in the markscheme",
                ).replace(
                    "{i0}",
                    str(subquestions[0]),
                )
                .replace(
                    "{i1}",
                    str(subquestions[1]),
                )
                .replace(
                    "{i2}",
                    str(subquestions[2]),
                ).replace(
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
                ).replace(
                    "{full_question_structure}",
                    json.dumps(question_to_subquestions, indent=4)
                )
            )
            response = question_detector.generate(
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
            detected_qs = parse_question_detector(response)
            if not all(
                v.isdigit() or (len(v) == 1 and v.isalpha()) for v in detected_qs
            ):
                continue
            paper_subquestions = [str(sq) for sq in subquestions[0:len(detected_qs)]]
            # ToDo: maybe turn this assertion into repeated LLM calls until they match
            assert paper_subquestions == detected_qs, \
                (f"Subquestions parsed from paper {paper_subquestions} do not match "
                 f"those parsed from the markscheme {detected_qs} for page {page_num}")
            breakpoint()
            [subquestions.pop(0) for _ in range(len(detected_qs))]
            num = latest_num
            for i, item in enumerate(detected_qs):
                if item.isalpha():
                    question_to_pages[f"{num}.{item}"] = [page_num]
                elif item.isdigit():
                    if len(detected_qs) == i+1 or detected_qs[i+1].isdigit():
                        question_to_pages[item] = [page_num]
                    num = int(item)
                else:
                    raise ValueError(f"Invalid type for question: {item}")
            latest_num = num
            all_detected_qs += detected_qs
        return _fill_missing_questions_n_pages(question_to_pages), latest_num

    question_to_pages, num_questions = parse_into_pages()
    question_to_pages = dict(
        sorted(question_to_pages.items(), key=lambda item: parse_key(item[0]))
    )
    with open(os.path.join(markscheme_dir, "question_to_pages.json"), "w+") as file:
        file.write(json.dumps(question_to_pages, indent=4))

    json_file_lock = threading.Lock()

    def parse_question(question_num: int):
        question_answer_parser = unify.Unify("o1@openai", cache=True)
        num_marks_detector = unify.Unify(
            "o1@openai",
            cache=True,
            system_message=NUM_MARKS_DETECTION,
        )
        sub_questions = [
            k.split(".")[-1] for k, v in question_to_pages.items()
            if k.startswith(str(question_num) + ".")
        ]
        pages = [
            v for k, v in question_to_pages.items()
            if (k == str(question_num) or k.startswith(str(question_num) + "."))
        ]
        pages = list(dict.fromkeys([item for sublist in pages for item in sublist]))
        current_text = ""
        for pg in pages:
            pg_text = reader.pages[pg - 1].extract_text()
            pg_text = prune_page_number(pg_text, pg, question_num)
            current_text += pg_text
        imgs = [all_images[pg - 1] for pg in pages]
        if sub_questions:
            sub_questions_expr = "the following sub-questions: " + ", ".join(sub_questions)
        else:
            sub_questions_expr = ("*no* sub-questions [(a), (b), (i) etc.], "
                                  "and so you should not look for or include any "
                                  "alphabetic sub-questions for this question.")
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
            )
            .replace(
                "{sub-questions}",
                sub_questions_expr,
            ),
        )
        qna = question_answer_parser.generate(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": current_text,
                        }
                    ] + [
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
        response = num_marks_detector.generate(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": qna,
                            }
                        ] + [
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
        num_marks = int(
            "".join([c for c in response.split("\n")[-1].lower() if c.isdigit()]),
        )
        questions[question_num] = {
            "text": qna,
            "num-marks": num_marks,
            "pages": pages,
            "sub-questions": sub_questions,
            "correctly_parsed": True
        }
        parsed = json.dumps(dict(sorted(questions.items())), indent=4)
        json_file_lock.acquire()
        with open(os.path.join(markscheme_dir, "parsed.json"), "w+") as file:
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
        img_dir = os.path.join(markscheme_dir, "imgs")
        os.makedirs(img_dir, exist_ok=True)
        fnames = [f"page{pg}.png" for pg in pages if pg in diagram_images]
        questions[question_num]["images"] = fnames
        for fname, img in zip(fnames, imgs):
            if not os.path.exists(fname):
                cv2.imwrite(os.path.join(img_dir, fname), img)

    unify.map(parse_question, list(range(1, num_questions + 1)))


if __name__ == "__main__":
    parse_pdf_into_papers_and_markschemes()
    subdirs = sorted(os.listdir(pdf_dir))

    def _parse(subdir: str):

        # paper
        target_paper_fpath = os.path.join(pdf_dir, subdir, "paper/parsed.json")
        if not os.path.exists(target_paper_fpath):
            parse_paper(int(subdir))

        target_q_to_pages_fpath = os.path.join(pdf_dir, subdir, "paper/question_to_pages.json")
        with open(target_q_to_pages_fpath) as f:
            target_q_to_pages = json.load(f)
        question_to_subquestions = dict()
        subquestions = list()
        for k in target_q_to_pages.keys():
            if "." not in k:
                question_to_subquestions[int(k)] = list()
                subquestions.append(int(k))
            else:
                q_num, q_letter = k.split(".")
                q_num = int(q_num)
                if q_num not in question_to_subquestions:
                    subquestions.append(q_num)
                    question_to_subquestions[q_num] = list()
                subquestions.append(q_letter)
                question_to_subquestions[q_num].append(q_letter)

        # markscheme
        target_markscheme_fpath = os.path.join(
            pdf_dir,
            subdir,
            "markscheme/parsed.json",
        )
        if not os.path.exists(target_markscheme_fpath):
            parse_markscheme(int(subdir), question_to_subquestions, subquestions)

    unify.map(_parse, subdirs)
