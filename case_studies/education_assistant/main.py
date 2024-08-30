# global
import os

# local
from case_studies.education_assistant.dataset_generation import \
    generate_dataset_from_past_paper

this_dir = os.path.dirname(os.path.realpath(__file__))

maths_paper_fname = \
    "resources/maths/169001-higher-tier-sample-assessment-materials_{}.pdf"

maths_paper_fpaths = [os.path.join(this_dir, maths_paper_fname.format(char))
                      for char in ("a", "b", "c")]
maths_dataset_fpaths = [fpath.replace(".pdf", ".jsonl") for fpath in maths_paper_fpaths]
for maths_paper_fpath, maths_dataset_fpath in zip(maths_paper_fpaths, maths_dataset_fpaths):
    generate_dataset_from_past_paper(maths_paper_fpath, maths_dataset_fpath)
