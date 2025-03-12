import os

def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.
    :param file_path: Path to the file.
    :return: True if the file exists, False otherwise.
    """
    return os.path.isfile(file_path)

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from the path.
    :param file_path: Path to the file.
    :return: The file extension.
    """
    return file_path.split('.')[-1]
