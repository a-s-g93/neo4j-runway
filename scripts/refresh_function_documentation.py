import os
import textwrap

from neo4j_runway import PyIngest
from neo4j_runway.utils import test_database_connection
from neo4j_runway.utils.data import load_data_dictionary_from_yaml, load_local_files

FUNCTION_DIR = [
    {
        "name": "pyingest",
        "functions": [
            {
                "function": PyIngest,
                "summary_file_path": "pyingest.md",
            }
        ],
        "file_path": "api/pyingest.md",
    },
    {
        "name": "utils",
        "functions": [
            {
                "function": test_database_connection,
                "summary_file_path": "utils.md",
            }
        ],
        "file_path": "api/utils/utils.md",
    },
    {
        "name": "data_loaders",
        "functions": [
            {
                "function": load_local_files,
                "summary_file_path": "load_local_files.md",
            },
            {
                "function": load_data_dictionary_from_yaml,
                "summary_file_path": "load_data_dictionary_from_yaml.md",
            },
        ],
        "file_path": "api/utils/data/data_loaders.md",
    },
]

MAX_TEXT_WIDTH: int = 60


def format_docstring(docstring: str) -> str:
    if not docstring:
        return ""
    # docstring = docstring.replace("        ", "    ")
    res = ""
    for line in docstring.split("\n"):
        res += (
            textwrap.fill(line, subsequent_indent="        ", width=MAX_TEXT_WIDTH)
            + "\n"
        )
    return res


def get_function_name_as_string(fn) -> str:
    return "## " + str(fn).split(" ")[1]


def read_summary(summary_file_path: str) -> str:
    with open(f"./docs/summaries/{summary_file_path}", "r") as f:
        return f.read()


def format_content(function_of_interest, summary_file_path: str) -> str:
    function_name_string = get_function_name_as_string(function_of_interest)
    summary_string = read_summary(summary_file_path) + "\n" if summary_file_path else ""
    content = f"""{function_name_string}
{summary_string}
{format_docstring(function_of_interest.__doc__).strip()}
"""
    return content


def create_front_matter(label: str, file_path: str) -> str:
    label = " ".join(x.capitalize() for x in label.split("_"))
    return f"""---
permalink: /{file_path[:-3].replace("_", "-")}/
title: {label}
toc: true
toc_label: {label}
toc_icon: "fa-solid fa-plane"
---
"""


def write_markdown_file(file_path: str, content: str, front_matter: str) -> None:
    base_path = "./docs/_pages/"
    path_parts = file_path.split("/")
    path_only = base_path + "/".join(path_parts[:-1])
    os.makedirs(path_only, exist_ok=True)
    with open(f"{base_path}{file_path}", "w") as f:
        f.write(front_matter)
        f.write(content)


if __name__ == "__main__":
    for page in FUNCTION_DIR:
        print(f"processing: {page}")
        to_write = ""
        front_matter = create_front_matter(
            label=page["name"],
            file_path=page["file_path"],
        )
        for f in page["functions"]:
            print(f"    processing: {f}")
            to_write += format_content(f["function"], f["summary_file_path"]) + "\n\n"

        write_markdown_file(
            file_path=page["file_path"], content=to_write, front_matter=front_matter
        )
