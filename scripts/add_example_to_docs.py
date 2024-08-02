import argparse
import os
from typing import Any, Dict
from urllib.request import urlopen

import nbformat
from nbconvert import MarkdownExporter


def drop_notebook_header(notebook):
    header_cell = notebook["cells"][0]
    header = header_cell["source"][2:]
    notebook["cells"] = notebook["cells"][1:]
    return header, notebook


def import_notebook(file_path: str) -> Any:
    """
    Loads a Python notebook from the root directory of "https://raw.githubusercontent.com/a-s-g93/neo4j-runway-examples/main/".
    Example notebooks MUST be stored in the repo "https://github.com/a-s-g93/neo4j-runway-examples".
    Outside examples will not be accepted.
    """
    print("importing file", file_path)
    url = f"https://raw.githubusercontent.com/a-s-g93/neo4j-runway-examples/main/{file_path}"
    response = urlopen(url).read().decode()

    return drop_notebook_header(nbformat.reads(response, as_version=4))


def write_example_page(
    notebook_dict: Dict[str, Any], notebook_name: str, header: str
) -> None:
    """
    The example will be saved to "docs/examples/notebook_name/notebook_name.md".
    svg files will be saved to "docs/examples/notebook_name/notebook_name_files/"
    Images will need to be manually added to "docs/examples/images/".
    """
    print("writing file", notebook_name)

    markdown_exporter = MarkdownExporter(template_name="markdown", preprocessors=[])

    (body, resources) = markdown_exporter.from_notebook_node(notebook_dict)

    docs_path = f"docs/examples/{notebook_name}/"
    img_folder = ""

    os.makedirs(docs_path, exist_ok=True)
    os.makedirs(f"{docs_path}{img_folder}", exist_ok=True)

    with open(f"{docs_path}{notebook_name}.md", "w") as f:
        f.write(
            f"""---
permalink: /examples/{notebook_name.replace("_", "-")}/
title: {header}
toc: true
toc_label:
toc_icon: "fa-solid fa-plane"
---
"""
        )
        f.write(body)
    for k, v in resources["outputs"].items():
        with open(f"{docs_path}{img_folder}{k}", "wb") as img:
            img.write(v)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--notebook_path", required=True)
    args = parser.parse_args()

    notebook_name = args.notebook_path.split("/")[-1][:-6]
    header, nb = import_notebook(file_path=args.notebook_path)
    write_example_page(notebook_dict=nb, notebook_name=notebook_name, header=header)
