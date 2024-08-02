import os
import textwrap

from neo4j_runway import PyIngest
from neo4j_runway.utils import test_database_connection

FUNCTION_DIR = [
    {
        "function": PyIngest,
        "file_path": "api/pyingest.md",
        "summary_file_path": "pyingest.md",
    },
    {
        "function": test_database_connection,
        "file_path": "api/utils.md",
        "summary_file_path": "utils.md",
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
    return str(fn).split(" ")[1]


def read_summary(summary_file_path: str) -> str:
    with open(f"./docs/summaries/{summary_file_path}", "r") as f:
        return f.read()


def format_content(function_of_interest, summary_file_path: str) -> str:
    function_name_string = get_function_name_as_string(function_of_interest)
    summary_string = read_summary(summary_file_path) + "\n" if summary_file_path else ""
    content = f"""{summary_string}
{format_docstring(function_of_interest.__doc__).strip()}
"""
    return content


def create_front_matter(label: str, file_path: str) -> str:
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
    for f in FUNCTION_DIR:
        print(f"processing: {f}")
        write_markdown_file(
            file_path=f["file_path"],
            content=format_content(f["function"], f["summary_file_path"]),
            front_matter=create_front_matter(
                label=get_function_name_as_string(f["function"]),
                file_path=f["file_path"],
            ),
        )
