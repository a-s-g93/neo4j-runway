import toml
import yaml


def get_current_version() -> str:
    with open("pyproject.toml", "r") as f:
        config = toml.load(f)
    return config["tool"]["poetry"]["version"]


def update_docs_config_yaml(new_version: str) -> None:
    with open("docs/_config.yml", "r") as f:
        config = yaml.safe_load(f)

    config["subtitle"] = "A Python package for Neo4j | v" + new_version

    with open("docs/_config.yml", "w") as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)


def update_package_init_version(new_version: str) -> None:
    with open("neo4j_runway/__init__.py", "r") as f:
        lines = f.readlines()
        new_file = []
        for line in lines:
            if line.startswith("__version__"):
                new_file.append(f"__version__ = '{new_version}'")
            else:
                new_file.append(line)
    with open("neo4j_runway/__init__.py", "w") as f:
        f.writelines(new_file)


if __name__ == "__main__":
    version = get_current_version()
    update_docs_config_yaml(new_version=version)
    update_package_init_version(new_version=version)
