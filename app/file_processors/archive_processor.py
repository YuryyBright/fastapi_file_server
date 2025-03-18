import zipfile
import os
import tempfile

import py7zr

from .base_processor import FileProcessor


class ArchiveProcessor(FileProcessor):
    """
    Processor for archive files. Extracts contents and delegates the search.
    """

    def __init__(self, file_path: str, processors: dict[str, FileProcessor]):
        """
        Initialize the archive processor with the file path, supported processors, and exact match configuration.
        :param file_path: Path to the archive file.
        :param processors: Dictionary of supported processors (extension -> class).
        :param exact_match: Whether to search for an exact match (default is partial).
        """
        self.file_path = file_path
        self.processors = processors

    def search(self, keyword: str, exact_match: bool = False) -> list[str]:
        """
        Extract the archive and search for the keyword in its files.
        :param keyword: The keyword to search for.
        :param exact_match: Whether to search for an exact match.
        :return: A list of lines containing the keyword.
        """
        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            if self.file_path.endswith('.zip'):
                with zipfile.ZipFile(self.file_path, 'r') as archive:
                    archive.extractall(temp_dir)
            elif self.file_path.endswith('.7z'):
                with py7zr.SevenZipFile(self.file_path, mode='r') as archive:
                    archive.extractall(temp_dir)
            else:
                raise ValueError("Unsupported archive format")

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    ext = file.split('.')[-1].lower()
                    processor_class = self.processors.get(ext)
                    if processor_class:
                        processor = processor_class(os.path.join(root, file))
                        results.extend(processor.search(keyword, exact_match))

        return results

    def read(self) -> str:
        """
        Read the content of a file from the extracted archive and return it as a string.
        :return: The content of the file as a string.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the archive contents
            if self.file_path.endswith('.zip'):
                with zipfile.ZipFile(self.file_path, 'r') as archive:
                    archive.extractall(temp_dir)
            elif self.file_path.endswith('.7z'):

                with py7zr.SevenZipFile(self.file_path, mode='r') as archive:
                    archive.extractall(temp_dir)
            else:
                print('processor.read(file)')
                raise ValueError("Unsupported archive format")

            content = []

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    ext = file.split('.')[-1].lower()
                    processor_class = self.processors.get(ext)
                    if processor_class:
                        processor = processor_class(os.path.join(root, file))
                        content.append(processor.read())
            return "\n".join(content)  # Об'єднуємо всі файли в єдиний текстовий блок