import os


def create_directory(full_file_path: str) -> None:
    """
    Create a directory specified in the full file path, if it doesn't exist.

    Parameters
    ----------
    full_file_path : str
        The whole thing.
    """

    if "/" in full_file_path:
        parts = full_file_path.split("/")
        _dir = "/".join(parts[:-1])
        os.makedirs(_dir, exist_ok=True)
