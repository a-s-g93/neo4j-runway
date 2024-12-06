from typing import Any, Dict


def get_dictionary_depth(dictionary: Any) -> int:
    """Get the max depth of a dictionary"""

    if isinstance(dictionary, dict):
        return 1 + (
            max(map(get_dictionary_depth, dictionary.values())) if dictionary else 0
        )
    return 0
