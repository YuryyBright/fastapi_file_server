from pprint import pprint

from file_processors.audio_processor import AudioProcessor
from file_processors.code_processor import CodeProcessor
from file_processors.image_processor import ImageProcessor
from file_processors.pdf_processor import PDFProcessor
from file_processors.presentation_processor import PresentationProcessor
from file_processors.text_processor import TextProcessor
from file_processors.utils.logger import logger
# from file_processors.video_processor import VideoProcessor
from file_processors.word_processor import WordProcessor
from file_processors.excel_processor import ExcelProcessor
from file_processors.archive_processor import ArchiveProcessor
# from utils.logger import logger
#

import os


import os

class SearchContext:
    """
    Context for managing file search operations and registered processors.
    """

    def __init__(self):
        self.processors = {}

    def register_processor(self, file_extension: str, processor_class):
        """
        Register a processor for a specific file type.
        :param file_extension: File extension to associate with the processor.
        :param processor_class: Processor class to handle the file type.
        """
        self.processors[file_extension] = processor_class

    def read_file(self, file_path: str) -> dict:
        """
        Read the content of a file using the appropriate processor.
        :param file_path: Path to the file.
        :return: Dictionary containing file metadata and content.
        """
        ext = file_path.split('.')[-1].lower()

        if ext not in self.processors:
            return {"status": "error", "message": f"No processor found for {ext} files"}

        try:

            processor = self.processors[ext](file_path)
            return  processor.read()  # Виклик read() у процесора
        except Exception as e:
            print(e)
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_type": ext,
                "error": str(e),
                "status": "error"
            }

    def search_in_file(self, file_path: str, keyword: str, exact_match: bool) -> dict:
        """
        Search for a keyword in a specified file and return detailed info.
        :param file_path: Path to the file.
        :param keyword: The keyword to search for.
        :param exact_match: Whether to search for an exact match.
        :return: Dictionary with file info and matches (if any).
        """
        ext = file_path.split('.')[-1].lower()
        if ext not in self.processors:
            return {"status": "error", "message": f"No processor found for {ext} files"}

        try:
            processor = self.processors[ext](file_path)
        except Exception as e:
            return {"status": "error", "message": str(e)}

        try:
            matches = processor.search(keyword, exact_match)
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_type": ext,
                "matches": matches,
                "status": "success" if matches else "no matches"
            }
        except Exception as e:
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_type": ext,
                "error": str(e),
                "status": "error"
            }

    def search_in_folder(self, folder_path: str, keyword: str, recursive: bool = True) -> list:
        """
        Search for a keyword in all supported files within a folder and return detailed results.
        :param folder_path: Path to the folder.
        :param keyword: The keyword to search for.
        :param recursive: Whether to search in subfolders recursively.
        :return: List of dictionaries with file paths, names, types, matches, or errors.
        """
        results = []
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                ext = file_name.split('.')[-1]
                if ext in self.processors:
                    file_result = self.search_in_file(file_path, keyword, exact_match=False)
                    results.append(file_result)
                    yield file_result
            if not recursive:
                break
        return results



if __name__ == "__main__":
    context = SearchContext()

    # Register file processors
    context.register_processor("mp3", AudioProcessor)
    # context.register_processor("mp4", VideoProcessor)
    context.register_processor("py", CodeProcessor)
    context.register_processor("pdf", PDFProcessor)
    context.register_processor("xlsx", ExcelProcessor)
    context.register_processor("pptx", PresentationProcessor)

    context.register_processor("txt", TextProcessor)
    context.register_processor("docx", WordProcessor)
    context.register_processor("doc", WordProcessor)

    context.register_processor("jpg", ImageProcessor)
    context.register_processor("png", ImageProcessor)
    context.register_processor("jpg", ImageProcessor)
    context.register_processor("jpeg", ImageProcessor)

    context.register_processor("zip", lambda path: ArchiveProcessor(path, context.processors))
    context.register_processor("7z", lambda path: ArchiveProcessor(path, context.processors))

    # Example usage
    file_path = "files\\1 (1).7z"
    keyword = "Молдова"
    exact_match = True
    logger.info(f"Searching for '{keyword}' in '{file_path}'...")
    results = context.read_file(file_path)
    pprint(results)
    # for result in results:
    #     logger.info(result)
