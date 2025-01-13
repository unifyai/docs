import os
import json
import unify


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
                answer = markscheme[question_num].get("text")
                questions_and_answers[question.get("text")] = answer
    return questions_and_answers


def main():
    qna = _load_questions_and_answers()


if __name__ == "__main__":
    main()
