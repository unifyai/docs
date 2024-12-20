import os
import cv2
import json
import base64
import numpy as np
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path

import unify
from prompts import *

fname = "169000-foundation-tier-sample-assessment-materials.pdf"
this_dir = os.path.dirname(__file__)
pdfs_dir = os.path.join(this_dir, "pdfs")
pdf_path = os.path.join(pdfs_dir, fname)
pdf_dir = os.path.join(pdfs_dir, fname[:-4])
reader = PdfReader(pdf_path)


def parse_pdf_into_papers_and_markschemes():
    paper_cover_text = "completetheboxesabovewithyourname,centrenumberandcandidatenumber."
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

    pdf_subdir = os.path.join(pdfs_dir, fname[:-4])
    os.makedirs(pdf_subdir, exist_ok=True)

    left_pointer = paper_cover_pages.pop(0)
    count = 1
    while paper_cover_pages or markscheme_cover_pages:
        count_dir = os.path.join(pdf_subdir, str(count))
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


def parse_paper(paper_num):
    question_detector = unify.Unify("gpt-4o@openai", cache=True,
                                    system_message=QUESTION_DETECTION)
    question_parser = unify.Unify("gpt-4o@openai", cache=True)
    diagram_detector = unify.Unify("gpt-4o@openai", cache=True)

    paper_dir = os.path.join(pdf_dir, str(paper_num), "paper")
    paper_path = paper_dir + ".pdf"

    reader = PdfReader(paper_path)
    questions = dict()

    def encode_image(image_path):
        _, buffer = cv2.imencode(".jpg", image_path)
        return base64.b64encode(buffer).decode("utf-8")

    def parse_into_pages():
        question_to_pages = dict()
        latest_num = 0
        latest_char = "`"
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            question_detector.set_system_message(
                QUESTION_DETECTION.replace(
                    "{n0}", str(latest_num + 1)
                ).replace(
                    "{n1}", str(latest_num + 2)
                ).replace(
                    "{n2}", str(latest_num + 3)
                ).replace(
                    "{c0}", chr(ord(latest_char) + 1)
                ).replace(
                    "{c1}", chr(ord(latest_char) + 2)
                ).replace(
                    "{c2}", chr(ord(latest_char) + 3)
                )
            )
            response = question_detector.generate(text)
            last_line = [v.strip() for v in response.split("\n")[-1].split(",")]
            previous_q_overflow = last_line[0].isalpha()
            if previous_q_overflow:
                question_to_pages[detected_numeric[-1]] += [page_num]
            detected_numeric = [int(v) for v in last_line if v.isnumeric()]
            if detected_numeric:
                latest_num = max(detected_numeric)
            last_question = last_line[-1]
            latest_char = "`" if last_question.isnumeric() else last_question
            for question in detected_numeric:
                question_to_pages[question] = [page_num]
        return question_to_pages, max(detected_numeric)

    all_images = [
        np.asarray(img.getdata()).reshape(img.size[1], img.size[0], 3).astype(np.uint8)
        for img in convert_from_path(paper_path)
    ]

    question_to_pages, num_questions = parse_into_pages()

    for question_num in range(1, num_questions + 1):
        pages = question_to_pages[question_num]
        current_text = "".join([reader.pages[pg].extract_text() for pg in pages])
        current_imgs = [all_images[pg] for pg in pages]
        question_parser.set_system_message(
            QUESTION_PARSER.replace(
                "{question_number}", str(question_num)
            ).replace(
                "{preceding}", str(question_num - 1)
            ).replace(
                "{subsequent}", str(question_num + 1)
            )
        )
        question_parsed = question_parser.generate(current_text)
        diagram_detector.set_system_message(
            DIAGRAM_DETECTION.replace(
                "{question_number}", str(question_num)
            ).replace(
                "{preceding}", str(question_num - 1)
            ).replace(
                "{subsequent}", str(question_num + 1)
            ),
        )
        diagram_response = diagram_detector.generate(
            messages=[
                {
                    "role": "user",
                    "content": [
                                   {
                                       "type": "text",
                                       "text": current_text
                                   },
                               ] + [
                                   {
                                       "type": "image_url",
                                       "image_url": {
                                           "url": f"data:image/jpeg;base64,{encode_image(img)}",
                                       },
                                   }
                                   for img in current_imgs],
                },
            ],
        )
        contains_diagram = "yes" in diagram_response.split("\n")[-1].strip().lower()
        questions[question_num] = {"text": question_parsed}
        if contains_diagram:
            img_dir = os.path.join(paper_dir, "imgs")
            os.makedirs(img_dir, exist_ok=True)
            fnames = [f"{question_num}_{i}.png" for i in range(len(current_imgs))]
            questions[question_num]["images"] = fnames
            for fname, img in zip(fnames, current_imgs):
                cv2.imwrite(os.path.join(img_dir, fname), img)

    parsed = json.dumps(questions, indent=4)
    with open(os.path.join(paper_dir, "parsed.json"), "w+") as file:
        file.write(parsed)


if __name__ == "__main__":
    parse_pdf_into_papers_and_markschemes()
    for subdir in sorted(os.listdir(pdf_dir)):
        target_fpath = os.path.join(pdf_dir, subdir, "paper/parsed.json")
        if not os.path.exists(target_fpath):
            parse_paper(int(subdir))
