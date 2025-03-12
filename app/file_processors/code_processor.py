from file_processors.base_processor import FileProcessor
import os


class CodeProcessor(FileProcessor):
    """
    Processor for code files (e.g., .py, .js, .java, etc.).
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def search(self, keyword: str) -> list[str]:
        """
        Search for a keyword in code files.
        :param keyword: The keyword to search for in the code file.
        :return: A list of lines containing the keyword.
        """
        results = []
        if not os.path.exists(self.file_path):  # Check if the file exists
            return [f"Error: File not found at {self.file_path}"]

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if keyword in line:
                        results.append(line.strip())
        except Exception as e:
            return [f"Error reading file: {str(e)}"]

        return results

    def read(self) -> str:
        """
        Read the entire content of the code file and return it as a string.
        :return: The full content of the code file.
        """
        if not os.path.exists(self.file_path):  # Check if the file exists
            return f"Error: File not found at {self.file_path}"

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()  # Read the entire file content
            return content.strip()  # Return the content as a string
        except Exception as e:
            return f"Error reading file: {str(e)}"
