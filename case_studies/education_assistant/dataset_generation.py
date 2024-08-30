import json
import openai
import jsonlines
from pypdf import PdfReader
from pydantic import BaseModel
# noinspection PyProtectedMember
from openai.lib._parsing._completions import type_to_response_format_param


def generate_dataset_from_past_paper(paper_fpath: str, dataset_fpath: str) -> None:

    assert dataset_fpath[-6:] == ".jsonl", \
        "dataset filepath must be a .jsonl file, " \
        "but filepath provides is: {}".format(dataset_fpath)

    pdf_content = "".join(["\nPAGE {}\n".format(i) + page.extract_text()
                           for i, page in enumerate(PdfReader(paper_fpath).pages)])
    client = openai.OpenAI()

    class NumberOfQuestions(BaseModel):
        value: int

    response_format = type_to_response_format_param(NumberOfQuestions)

    system_prompt =\
        "You will be given a maths exam paper and a detailed mark scheme, which have " \
        "been extracted from a PDF. Your task is to determine the total number of " \
        "questions in the paper, and return this number. The questions are " \
        "explicitly numbered in the paper, and so counting should not be needed, " \
        "simply read the number corresponding to the final question, and return the " \
        "value as a number (not a word), and nothing else."
    # noinspection PyTypeChecker
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pdf_content}
        ],
        response_format=response_format
    )
    num_questions = json.loads(response.choices[0].message.content)["value"]

    print("paper contains {} questions".format(num_questions))

    class QuestionAnswerPair(BaseModel):
        full_question: str
        full_answer: str
        answerable: bool

    response_format = type_to_response_format_param(QuestionAnswerPair)

    qna_pairs = list()
    for i in range(1, num_questions+1):
        system_prompt =\
            "You will be given a maths exam paper and a detailed mark scheme, which " \
            "have been extracted from a PDF. Your task is to extract question {} in a " \
            "totally unmodified manner and also the corresponding answer from the mark " \
            "scheme for question {} only, also in a fully unmodified and exhaustive manner," \
            "as per the json format requested. The question will appear in the earlier pages of the " \
            "document, and the answer will appear in the later pages of the " \
            "document in the mark scheme section, with the question numbers aligned to each answer in the mark scheme. " \
            "Some questions might not be answerable in a purely text-based manner." \
            "For example the question might require drawing on a chart or graph," \
            "or the question might refers to some shape, image, table or chart. " \
            "Otherwise, the question text might simply seem incomplete in some " \
            "way, where the question could not be answered based on the question text alone. " \
            "In such cases, you should set the answerable response as " \
            "False, otherwise if it CAN be answered based on the purely text-based question, " \
            "then answerable should be set as True.".format(i, i)
        # noinspection PyTypeChecker
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pdf_content}
            ],
            response_format=response_format
        )
        response = json.loads(response.choices[0].message.content)
        print("\nQUESTION {}".format(i))
        if not response["answerable"]:
            print("\nSKIPPING:\nQ: {}".format(response["full_question"]))
            print("--------")
            continue
        del response["answerable"]
        print("\nADDING:\nQ: {}\nA: {}".format(
            response["full_question"], response["full_answer"]))
        print("--------")
        qna_pairs.append(response)

        with jsonlines.open(dataset_fpath, mode='w') as writer:
            writer.write_all(qna_pairs)
