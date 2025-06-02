from app.file_processors.base_processor import FileProcessor, TextSearcher


class TextProcessor(FileProcessor):
    """
    Processor for plain text files.
    This class provides functionality to search for keywords and read the entire text content from a plain text file.
    """

    def __init__(self, file_path: str):
        """
        Initialize the TextProcessor with the file path.
        :param file_path: Path to the plain text file.
        """
        self.file_path = file_path

    def search(self, keyword: str, exact_match: bool = False) -> list[str]:
        """
        Search for a keyword in the plain text file.
        :param keyword: The keyword to search for in the text file.
        :param exact_match: Whether to search for an exact match (default is False for partial matches).
        :return: A list of lines containing the keyword.
        """
        results = []
        with open(self.file_path, 'r', encoding='utf-8') as file:
            # Iterate over each line in the file
            for line in file:
                if keyword in line:
                    results.append(line.strip())  # Add line to results if keyword is found

        # Optionally, use an external TextSearcher to process the result further
        return TextSearcher.search_text("\n".join(results), keyword, exact_match)

    def read(self) -> str:
        """
        Read the entire content of the plain text file and return it as a single string.
        :return: The text content of the entire file.
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return file.read()  # Return the entire content of the file as a string
