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


def _test_examples(examples: List[str], executable: callable) -> Dict[str, Union[True, str]]:
    results = dict()
    for example in examples:
        try:
            executable(example)
            val = True
        except Exception as e:
            val = str(e)
        results[example] = val
    return results


def _capture_exec_output(code_str: str) -> Any:
    with io.StringIO() as buf, redirect_stdout(buf):
        exec(code_str)
        output = buf.getvalue()
    return output


def _check_rest_api_failures(ret: str) -> None:
    ret_dict = json.loads(ret)
    if "detail" in ret_dict:
        assert "Invalid API key" not in ret_dict["detail"], "Invalid API key"


def _test_python_examples(examples: List[str]) -> Dict[str, Union[True, str]]:
    def _test_python_fn(str_in: str) -> None:
        ret = _capture_exec_output(str_in)
        if "import requests" in str_in:
            _check_rest_api_failures(ret)
    return _test_examples(examples, _test_python_fn)


def _test_shell_examples(examples: List[str]) -> Dict[str, Union[True, str]]:
    def _test_shell_fn(str_in: str) -> None:
        ret = os.popen(str_in).read()
        _check_rest_api_failures(ret)
    return _test_examples(examples, _test_shell_fn)


def get_mdx_filepaths() -> List[str]:
    mdx_filepaths = list()
    for root, dirs, files in os.walk(os.path.abspath(os.path.join(this_dir, "../"))):
        if "api-reference" in root:
            continue
        for filename in files:
            if ".mdx" in filename:
                mdx_filepaths.append(os.path.abspath(os.path.join(root, filename)))
    return mdx_filepaths


def run_test(filepath: str) -> Tuple[Dict, Dict]:

    # extract contents
    with open(filepath) as f:
        content = f.read()

    # test Python examples
    python_examples = _extract_python_examples(content)
    python_results = _test_python_examples(python_examples)

    # test Shell examples
    shell_examples = _extract_shell_examples(content)
    shell_results = _test_shell_examples(shell_examples)

    return python_results, shell_results


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


def save_results(results: Dict[str, Dict[str, Dict[str, Union[True, str]]]], fpath: str) -> None:
    json_str = json.dumps(results)
    with open(fpath, "w") as file:
        file.write(json_str)


def print_results(results: Dict[str, Dict[str, Dict[str, Union[True, str]]]], verbose: bool = False) -> None:
    for section_name, section_results in results.items():
        print(section_name)
        for page_name, page_results in section_results.items():
            print(" "*4 + page_name)
            for language_name, language_results in page_results.items():
                print(" "*8 + language_name)
                for i, (codeblock, result) in enumerate(language_results.items()):
                    result_str = "passed" if result is True else "failed"
                    print(" " * 12 + str(i) + ": " + result_str)
                    if verbose:
                        print(" " * 12 + codeblock.replace("\n", "\n" + " "*12))
                        if result is not True:
                            print(" " * 12 + result)
                        print("")
