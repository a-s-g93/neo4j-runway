import os
from typing import Any


def read_environment(key: str) -> Any:
    if key in os.environ.keys():
        return os.environ.get(key)
    else:
        return None
