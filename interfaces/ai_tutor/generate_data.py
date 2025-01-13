import os
import json
import unify
from prompts import *

num_examples = 5


def _load_questions_and_answers():
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

                questions_and_answers[question.get("text")] = (answer, marks)
    return questions_and_answers


def main():
    data = dict()
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    generation_client = unify.Unify("o1@openai", n=num_examples, cache=True)
    qna = _load_questions_and_answers()
    for question, (answer, marks) in qna.items():
        targets = dict()
        for target in range(marks+1):
            response = generation_client.generate(
                system_message=GENERATE_RESPONSE_PROMPT.replace(
                    "{target}", str(target)
                ).replace(
                    "{num_marks}", str(marks)
                ).replace(
                    "{question}", question
                ).replace(
                    "{answer}", answer
                ),
                return_full_completion=True
            )
            generated_answers = list()
            for choice in response.choices:
                generated_answers.append(
                    choice.message.content.split("nswer:")[-1].lstrip("\n")
                )
            targets[target] = generated_answers
        data[question] = targets
        # incremental file writing
        with open(data_dir, "w+") as f:
            f.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()
