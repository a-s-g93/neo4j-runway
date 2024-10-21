from typing import Any, List


def red(content: str) -> str:
    """format string to be printed red"""
    return f"\033[91m{content}\033[00m"


def green(content: str) -> str:
    """format string to be printed green"""
    return f"\033[92m{content}\033[00m"


def cyan(content: str) -> str:
    """format string to be printed cyan"""
    return f"\033[96m{content}\033[00m"


def bold(content: str) -> str:
    """format string to be printed bold"""
    return f"\033[1m{content}\033[00m"


def italics(content: str) -> str:
    """format string to be printed in italics"""
    return f"\x1b[3m{content}\x1b[0m"


def pretty_list(header: str, content: List[Any], cols: int = 1) -> str:
    """return a list as a bulleted list under a header"""

    if cols > 2:
        cols = 2

    max_len = 0
    # only check left col
    for i in range(0, len(content), cols):
        if len(content[i]) > max_len:
            max_len = len(content[i])

    res = header
    for i in range(0, len(content), cols):
        white_space_size = max_len - len(content[i])
        to_add = f"\n* {content[i]}{' ' * (white_space_size + 3)}"
        if cols > 1 and i + 1 < len(content):
            to_add += f"* {content[i+1]}"

        res += to_add

    return res


def add_indent(content: str, spaces: int = 4) -> str:
    """add an indent to the provided string"""

    lines = content.split("\n")
    lines = [(" " * spaces) + l for l in lines]
    return "\n".join(lines)
