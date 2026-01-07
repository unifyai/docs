import os
import json
from tests.helpers import (
    get_mdx_filepaths,
    run_test,
    group_and_order_results,
    save_results,
    print_results,
    prune_successes_from_results,
)

this_dir = os.path.dirname(os.path.realpath(__file__))


def test_all():
    mdx_filepaths = get_mdx_filepaths()
    results = dict()
    all_passed = True
    results_fpath = os.path.join(this_dir, "results.json")
    results_pruned_fpath = os.path.join(this_dir, "results_pruned.json")
    if os.path.exists(results_fpath):
        results = json.load(open(results_fpath))
    else:
        for mdx_filepath in mdx_filepaths:
            python_results, shell_results, all_passed = run_test(mdx_filepath)
            mdx_filepath_short = mdx_filepath.split("docs/")[-1].split(".mdx")[0]
            results[mdx_filepath_short] = {
                "python": python_results,
                "shell": shell_results,
            }
        results = group_and_order_results(results)
        results_pruned = prune_successes_from_results(results.copy())
        save_results(results, results_fpath)
        save_results(results_pruned, results_pruned_fpath)
    print_results(results)
    assert all_passed, "The tests did not all pass, see logs above."
