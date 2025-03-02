import os
import cv2
import wget
import json
import shutil
import base64
import requests
import random
random.seed(0)
from pydantic import BaseModel, create_model

import unify
unify.set_seed(0)

unify.activate("EdTech", overwrite=True)

# Download Data #
# ------------- #

# Download the dataset
fname = "labelled_data.json"
if not os.path.exists(fname):
    wget.download("https://raw.githubusercontent.com/unifyai/demos/refs/heads/main/ai_tutor/data/labelled_data.json")
with open(fname, "r") as f:
    labelled_data = json.load(f)

def download_github_subdir(owner, repo, subdir_path, branch="main", dst_dir="downloaded"):
    """
    Recursively download a subdirectory (and its entire contents) from a public GitHub repo.

    :param owner: GitHub username or organization name
    :param repo:  GitHub repository name
    :param subdir_path: Path to the subdirectory in the repo (e.g., "folder/subfolder")
    :param branch: Branch name or tag (default: "main")
    :param dst_dir: Local directory where content will be saved
    """
    # Build the GitHub API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{subdir_path}?ref={branch}"

    try:
        # Get JSON directory listing
        response = requests.get(api_url)
        response.raise_for_status()
        items = response.json()

        # If the result is a single file, items might be a dict instead of a list
        if isinstance(items, dict) and items.get("type") == "file":
            items = [items]  # Convert to list for consistency

        for item in items:
            item_type = item["type"]
            item_name = item["name"]
            item_path = item["path"]

            if item_type == "dir":
                # Create local folder
                local_dir = os.path.join(dst_dir, item_path)
                os.makedirs(local_dir, exist_ok=True)
                # Recursively get contents of this folder
                download_github_subdir(
                    owner=owner,
                    repo=repo,
                    subdir_path=item_path,
                    branch=branch,
                    dst_dir=dst_dir
                )
            elif item_type == "file":
                download_url = item["download_url"]
                local_file_path = os.path.join(dst_dir, item_path)

                # Create directories for the file if they don't exist
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                print(f"Downloading file: {item_path}")
                file_resp = requests.get(download_url)
                file_resp.raise_for_status()

                with open(local_file_path, "wb") as f:
                    f.write(file_resp.content)
            else:
                # If it's a symlink or submodule, you can handle that here if needed
                print(f"Skipping unsupported item type: {item_type} - {item_name}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e} - {api_url}")
    except Exception as e:
        print(f"Error: {e} - {api_url}")

# Download the Images
if not os.path.exists("pdfs"):
    download_github_subdir(
        owner="unifyai",
        repo="demos",
        subdir_path="ai_tutor/pdfs/GCSE_(9–1)_Mathematics",
        branch="main",
        dst_dir=""
    )
    shutil.move("ai_tutor/pdfs", "pdfs")

def encode_image(image):
    _, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("utf-8")



def create_dataset():
    logs = list()
    example_id = 0
    for question, data in labelled_data.items():
        data = data.copy()
        data["available_marks_total"] = data["available_marks"]
        data["available_marks"] = data["mark_breakdown"]
        del data["mark_breakdown"]
        if not isinstance(data["question_components"], dict):
            data["question_components"] = {"_": data["question_components"]}
        data["sub_questions"] = data["question_components"]
        del data["question_components"]
        if not isinstance(data["markscheme"], dict):
            data["markscheme"] = {"_": data["markscheme"]}
        subject_dir = os.path.join("pdfs", data["subject"].replace(" ", "_"))
        paper_dir = os.path.join(subject_dir, data["paper_id"].replace(" ", "_"))
        q_imgs_dir = os.path.join(paper_dir, "paper/imgs")
        q_img_fpaths = [
            f"{q_imgs_dir}/page{pg}.png" for pg in data["question_pages"]
        ]
        question_imgs = [
            encode_image(cv2.imread(fpath, -1)) for fpath in q_img_fpaths
        ]
        m_imgs_dir = os.path.join(paper_dir, "markscheme/imgs")
        m_img_fpaths = [
            f"{m_imgs_dir}/page{pg}.png" for pg in data["markscheme_pages"]
        ]
        markscheme_imgs = [
            encode_image(cv2.imread(fpath, -1)) for fpath in m_img_fpaths
        ]
        for mark, ans_n_rat in data.items():
            if not all(c.isdigit() for c in mark):
              continue
            mark_int = int(mark)
            if "answer" in ans_n_rat:
              student_answer = {"_": ans_n_rat["answer"]}
              correct_marks = {
                  "_": {
                      "marks": ans_n_rat["marks"],
                      "rationale": ans_n_rat["rationale"]
                  }
              }
            else:
              student_answer = {k: v["answer"] for k, v in ans_n_rat.items()}
              correct_marks = {
                  k: {
                      "marks": v["marks"],
                      "rationale": v["rationale"]
                  }
                  for k, v in ans_n_rat.items()
              }
              correct_marks_breakdown = {
                  k: v["marks"] for k, v in ans_n_rat.items()
              }
            per_question_breakdown = {
                k: {
                    "sub_question": q,
                    "available_marks": am,
                    "student_answer": sa,
                    "markscheme": ms,
                    "correct_marks": cm
                } for (k, q), am, sa, ms, cm in zip(
                    data["sub_questions"].items(),
                    data["available_marks"].values(),
                    student_answer.values(),
                    data["markscheme"].values(),
                    correct_marks.values()
                )
            }
            per_question_breakdown["question"] = question
            logs.append(
                {
                    **{k: v for k, v in data.items() if not k.isdigit()},
                    **{
                        "example_id": example_id,
                        "question": question,
                        "student_answer": student_answer,
                        "correct_marks": correct_marks,
                        "correct_marks_total": mark_int,
                        "per_question_breakdown": per_question_breakdown,
                        "question_pages": question_imgs,
                        "markscheme_pages": markscheme_imgs,
                    }
                }
            )
            example_id += 1
    return logs

data = create_dataset()
dataset = unify.Dataset(data, name="TestSet").upload()
