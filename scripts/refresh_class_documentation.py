import inspect
import textwrap
from typing import List
import os

from neo4j_runway import DataModel, IngestionGenerator, Discovery, LLM, GraphDataModeler

# ALL DOCUMENTED CLASSES MUST BE LISTED HERE!
# Map features
#   * class             : The Neo4j Runway Class being documented.
#   * file_path         : The file path from ./docs/_pages/ to write the file to. 
#                         Also the site extension location ex: api/data_model.md lives at http://site.com/neo4j-runway/api/data-model/
#   * summary_file_path : The file path from ./docs/summaries/ of the summary Markdown file, if any/. 
#                         This text will be injected below the page header before Class methods and properties are displayed.

CLASS_DIR = [
    {"class": DataModel, "file_path": "api/data_model.md", "summary_file_path": "data_model.md"},
    {"class": IngestionGenerator, "file_path": "api/ingestion_generator.md", "summary_file_path": ""},
    {"class": Discovery, "file_path": "api/discovery.md", "summary_file_path": ""},
    {"class": GraphDataModeler, "file_path": "api/graph_data_modeler.md", "summary_file_path": ""},
    {"class": LLM, "file_path": "api/llm.md", "summary_file_path": ""},
]

MAX_TEXT_WIDTH = 60

def format_docstring(docstring: str) -> str:
    if not docstring: return ""
    docstring = docstring.replace("        ", "    ")
    res = ""
    for line in docstring.split("\n"):
        res+=(textwrap.fill(line, subsequent_indent="        ", width=MAX_TEXT_WIDTH) + "\n")
    return res

def get_method_docstrings_of_class(class_of_interest) -> List[str]:
    return [(m[0], format_docstring(m[1].__doc__)) for m in inspect.getmembers(class_of_interest, predicate=inspect.isfunction) if "BaseModel" not in str(m[1]) and (not m[0].startswith("_") or m[0] == "__init__")]

def get_properties_of_class(class_of_interest) -> List[str]:
    ignored_props = {"__fields_set__", "model_extra", "model_fields_set"}
    return [(m[0], format_docstring(m[1].__doc__)) for m in inspect.getmembers(class_of_interest) if "BaseModel" not in str(m[1]) and "property" in str(m[1]) and m[0] not in ignored_props]

def get_class_name_as_string(class_of_interest) -> str:
    return str(class_of_interest).split(".")[-1][:-2]

def read_summary(summary_file_path: str) -> str:
     with open(f"./docs/summaries/{summary_file_path}", "r") as f:
          return f.read()
     
def format_content(class_of_interest, summary_file_path: str) -> str:
    class_name_string = get_class_name_as_string(class_of_interest)
    methods_as_strings = get_method_docstrings_of_class(class_of_interest)
    properties_as_strings = get_properties_of_class(class_of_interest)
    summary_string = read_summary(summary_file_path)+"\n" if summary_file_path else ""
    content = f"""# {class_name_string}
{summary_string}

## Class Methods

"""

    for m in methods_as_strings:
        content+=f"""
{m[0]}
---
{m[1].strip()}

"""
    if len(properties_as_strings) > 0: content+="\n\n## Class Properties\n\n"
    for p in properties_as_strings:
        content+=f"""
{p[0]}
---
{p[1].strip()}

"""
    return content

def write_markdown_file(file_path: str, content: str) -> None:
    base_path = "./docs/_pages/"
    path_parts = file_path.split("/")
    path_only = base_path + "/".join(path_parts[:-1])
    os.makedirs(path_only, exist_ok=True)
    with open(f"{base_path}{file_path}", "w") as f:
                f.write(f"""---
permalink: /{file_path[:-3].replace("_", "-")}/
---
""")
                f.write(content)  

if __name__ == "__main__":
    for m in CLASS_DIR:
        print(f"processing: {m}")
        write_markdown_file(file_path=m["file_path"], content=format_content(m["class"], m["summary_file_path"]))