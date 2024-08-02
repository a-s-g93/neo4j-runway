import inspect
import os
import textwrap
from typing import List

import regex as re

from neo4j_runway import (
    DataModel,
    Discovery,
    GraphDataModeler,
    UserInput,
)
from neo4j_runway.code_generation import (
    LoadCSVCodeGenerator,
    PyIngestConfigGenerator,
    StandardCypherCodeGenerator,
)
from neo4j_runway.database import Neo4jGraph
from neo4j_runway.llm.openai import OpenAIDataModelingLLM, OpenAIDiscoveryLLM

# ALL DOCUMENTED CLASSES MUST BE LISTED HERE!
# Map features
#   * class             : The Neo4j Runway Class being documented.
#   * file_path         : The file path from ./docs/_pages/ to write the file to.
#                         Also the site extension location ex: api/data_model.md lives at http://site.com/neo4j-runway/api/data_model/
#   * summary_file_path : The file path from ./docs/summaries/ of the summary Markdown file, if any/.
#                         This text will be injected below the page header before Class methods and properties are displayed.

CLASS_DIR = [
    {
        "class": DataModel,
        "file_path": "api/data_model.md",
        "summary_file_path": "data_model.md",
    },
    {
        "class": Discovery,
        "file_path": "api/discovery.md",
        "summary_file_path": "discovery.md",
    },
    {
        "class": GraphDataModeler,
        "file_path": "api/graph_data_modeler.md",
        "summary_file_path": "graph_data_modeler.md",
    },
    {
        "class": OpenAIDiscoveryLLM,
        "file_path": "api/llm/openai_discovery_llm.md",
        "summary_file_path": "openai_discovery_llm.md",
    },
    {
        "class": OpenAIDataModelingLLM,
        "file_path": "api/llm/openai_data_modeling_llm.md",
        "summary_file_path": "openai_data_modeling_llm.md",
    },
    {
        "class": Neo4jGraph,
        "file_path": "api/database/neo4j_graph.md",
        "summary_file_path": "neo4j_graph.md",
    },
    {
        "class": UserInput,
        "file_path": "api/inputs.md",
        "summary_file_path": "inputs.md",
    },
    {
        "class": PyIngestConfigGenerator,
        "file_path": "api/code_generator/pyingest_config_generator.md",
        "summary_file_path": "pyingest_config_generator.md",
    },
    {
        "class": LoadCSVCodeGenerator,
        "file_path": "api/code_generator/load_csv_code_generator.md",
        "summary_file_path": "load_csv_code_generator.md",
    },
    {
        "class": StandardCypherCodeGenerator,
        "file_path": "api/code_generator/standard_cypher_code_generator.md",
        "summary_file_path": "standard_cypher_code_generator.md",
    },
]

MAX_TEXT_WIDTH: int = 60


def format_docstring(docstring: str) -> str:
    if not docstring:
        return ""
    docstring = docstring.replace("        ", "    ")
    res = ""
    for line in docstring.split("\n"):
        res += (
            textwrap.fill(line, subsequent_indent="        ", width=MAX_TEXT_WIDTH)
            + "\n"
        )
    return res


def get_method_docstrings_of_class(class_of_interest) -> List[str]:
    return [
        (m[0], format_docstring(m[1].__doc__))
        for m in inspect.getmembers(class_of_interest, predicate=inspect.isfunction)
        if "BaseModel" not in str(m[1])
        and (not m[0].startswith("_") or m[0] == "__init__")
    ]


def get_attributes(class_of_interest) -> str:
    parts = re.split("(   Attributes)", class_of_interest.__doc__)
    parts[0] = parts[0].replace("   ", "")
    combined = "".join(parts)
    res = ""
    for line in combined.split("\n"):
        res += (
            textwrap.fill(line, subsequent_indent="        ", width=MAX_TEXT_WIDTH)
            + "\n"
        )
    return res


def get_properties_of_class(class_of_interest) -> List[str]:
    ignored_props = {"__fields_set__", "model_extra", "model_fields_set"}
    return [
        (m[0], format_docstring(m[1].__doc__))
        for m in inspect.getmembers(class_of_interest)
        if "BaseModel" not in str(m[1])
        and "property" in str(m[1])
        and m[0] not in ignored_props
        and not m[0].startswith("_")
    ]


def get_class_name_as_string(class_of_interest) -> str:
    return str(class_of_interest).split(".")[-1][:-2]


def read_summary(summary_file_path: str) -> str:
    with open(f"./docs/summaries/{summary_file_path}", "r") as f:
        return f.read()


def format_content(class_of_interest, summary_file_path: str) -> str:
    class_name_string = get_class_name_as_string(class_of_interest)
    methods_as_strings = get_method_docstrings_of_class(class_of_interest)
    properties_as_strings = get_properties_of_class(class_of_interest)
    summary_string = read_summary(summary_file_path) + "\n" if summary_file_path else ""
    attributes = get_attributes(class_of_interest=class_of_interest)
    content = f"""{summary_string}
{attributes}

## Class Methods

"""

    for m in methods_as_strings:
        content += f"""
### {m[0]}
{m[1].strip()}

"""
    if len(properties_as_strings) > 0:
        content += "\n\n## Class Properties\n\n"
    for p in properties_as_strings:
        content += f"""
### {p[0]}
{p[1].strip()}

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
    for m in CLASS_DIR:
        print(f"processing: {m}")
        write_markdown_file(
            file_path=m["file_path"],
            content=format_content(m["class"], m["summary_file_path"]),
            front_matter=create_front_matter(
                label=get_class_name_as_string(m["class"]), file_path=m["file_path"]
            ),
        )
