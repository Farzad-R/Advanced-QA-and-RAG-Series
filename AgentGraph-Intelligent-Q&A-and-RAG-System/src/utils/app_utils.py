import os
from pyprojroot import here


def create_directory(directory_path: str) -> None:
    """
    Create a directory if it does not exist.

    Parameters:
        directory_path (str): The path of the directory to be created.

    Example:
    ```python
    create_directory("/path/to/new/directory")
    ```

    """
    if not os.path.exists(here(directory_path)):
        os.makedirs(here(directory_path))
