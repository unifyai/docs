import os
import io
import json
from contextlib import redirect_stdout
from typing import List, Dict, Tuple, Union, Any

this_dir = os.path.dirname(os.path.realpath(__file__))


def _extract_examples(file_str: str, language: str) -> List[str]:
    chunks = file_str.split("```" + language)[1:]
    return [chunk.split("```")[0] for chunk in chunks]


def _extract_python_examples(file_str: str) -> List[str]:
    return _extract_examples(file_str, "python")


def _extract_shell_examples(file_str: str) -> List[str]:
    return _extract_examples(file_str, "shell")


def _replace_api_key_placeholders(example: str) -> str:
    example = example.replace("$UNIFY_KEY", os.environ.get("UNIFY_KEY"))
    example = example.replace("UNIFY_KEY", os.environ.get("UNIFY_KEY"))
    return example


def _capture_exec_output(code_str: str) -> Any:
    with io.StringIO() as buf, redirect_stdout(buf):
        exec(code_str)
        output = buf.getvalue()
    return output


def _check_rest_api_failures(ret: str) -> None:
    ret_dict = json.loads(ret)
    if "detail" in ret_dict:
        assert "Invalid API key" not in ret_dict["detail"], "Invalid API key"


def _test_python_examples(examples: List[str]) -> Tuple[Dict[str, Union[True, str]], bool]:
    def _test_python_fn(str_in: str) -> None:
        ret = _capture_exec_output(str_in)
        if "import requests" in str_in:
            _check_rest_api_failures(ret)
    all_passed = True
    results = dict()
    for example in examples:
        if "<" in example and ">" in example:
            # there is a placeholder, not runnable
            continue
        example_w_key = "import unify\n" + _replace_api_key_placeholders(example)
        try:
            _test_python_fn(example_w_key)
            val = True
        except Exception as e:
            val = str(e)
            all_passed = False
        results[example] = val
    return results, all_passed


def _test_shell_examples(examples: List[str]) -> Tuple[Dict[str, Union[True, str]], bool]:
    def _test_shell_fn(str_in: str) -> None:
        ret = os.popen(str_in).read()
        _check_rest_api_failures(ret)
    all_passed = True
    results = dict()
    for example in examples:
        if "<" in example and ">" in example:
            # there is a placeholder, not runnable
            continue
        example_w_key = _replace_api_key_placeholders(example)
        try:
            _test_shell_fn(example_w_key)
            val = True
        except Exception as e:
            val = str(e)
            all_passed = False
        results[example] = val
    return results, all_passed


def get_mdx_filepaths() -> List[str]:
    mdx_filepaths = list()
    for root, dirs, files in os.walk(os.path.abspath(os.path.join(this_dir, "../"))):
        if "api-reference" in root:
            continue
        for filename in files:
            if ".mdx" in filename:
                mdx_filepaths.append(os.path.abspath(os.path.join(root, filename)))
    return mdx_filepaths


def run_test(filepath: str) -> Tuple[Dict, Dict, bool]:

    # extract contents
    with open(filepath) as f:
        content = f.read()

    # test Python examples
    python_examples = _extract_python_examples(content)
    python_results, all_python_passed = _test_python_examples(python_examples)

    # test Shell examples
    shell_examples = _extract_shell_examples(content)
    shell_results, all_shell_passed = _test_shell_examples(shell_examples)

    return python_results, shell_results, all_python_passed and all_shell_passed


def group_and_order_results(results: Dict[str, Dict[str, Union[True, str]]])\
        -> Dict[str, Dict[str, Dict[str, Union[True, str]]]]:
    with open(os.path.join(this_dir, "../mint.json")) as file:
        mint_contents = file.read()
    mint_json = json.loads(mint_contents)
    navigation = mint_json["navigation"]
    results_out = dict()
    for i, group in enumerate(navigation):
        if group["group"] in ("", "API Reference"):
            continue
        results_out[group["group"]] = dict()
        for j, page in enumerate(group["pages"]):
            results_out[group["group"]][page] = results[page]
    return results_out


def prune_successes_from_results(results: Dict) -> Dict:
    keys_to_delete = list()
    for key, value in results.items():
        if isinstance(value, dict):
            prune_successes_from_results(value)
        if value in (True, {}):
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del results[key]
    return results


def save_results(results: Dict[str, Dict[str, Dict[str, Union[True, str]]]], fpath: str) -> None:
    json_str = json.dumps(results, indent=4)
    with open(fpath, "w") as file:
        file.write(json_str)


def print_results(results: Dict[str, Dict[str, Dict[str, Union[True, str]]]],
                  failed_only: bool = True,
                  verbose: bool = True,
                  print_exception: bool = False) -> None:
    for section_name, section_results in results.items():
        print(section_name)
        for page_name, page_results in section_results.items():
            print(" "*4 + page_name)
            for language_name, language_results in page_results.items():
                print(" "*8 + language_name)
                for i, (codeblock, result) in enumerate(language_results.items()):
                    passed = result is True
                    if passed and failed_only:
                        continue
                    result_str = "passed" if passed else "failed"
                    print(" " * 12 + str(i) + ": " + result_str)
                    if verbose:
                        print(" " * 12 + codeblock.replace("\n", "\n" + " "*12))
                        if result is not True and print_exception:
                            print(" " * 12 + result)
                        print("")
