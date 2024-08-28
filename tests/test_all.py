import os
import json
from tests.helpers import get_mdx_filepaths, run_test, group_and_order_results, save_results, print_results

this_dir = os.path.dirname(os.path.realpath(__file__))


def test_all():
    mdx_filepaths = get_mdx_filepaths()
    results = dict()
    results_fpath = os.path.join(this_dir, "results.json")
    if os.path.exists(results_fpath):
        results = json.load(open(results_fpath))
    else:
        for mdx_filepath in mdx_filepaths:
            python_results, shell_results = run_test(mdx_filepath)
            mdx_filepath_short = mdx_filepath.split("unify-docs/")[-1].split(".mdx")[0]
            results[mdx_filepath_short] = {"python": python_results, "shell": shell_results}
        results = group_and_order_results(results)
        save_results(results, results_fpath)
    print_results(results)
