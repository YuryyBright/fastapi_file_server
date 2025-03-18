import easyocr
import numpy as np
from PIL import Image
from file_processors.base_processor import FileProcessor, TextSearcher
import sys
import os
import contextlib


class ImageProcessor(FileProcessor):
    """
    Processor for image files, performing text extraction using EasyOCR.
    """

    def __init__(self, file_path: str):
        """
        Initialize the image processor with the file path and configuration for exact match.
        :param file_path: Path to the image file.
        :param exact_match: Whether to search for an exact match (default is partial).
        """
        self.file_path = file_path

        # Suppress the EasyOCR GPU warning message by redirecting stderr
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stderr(devnull):
                # Initialize EasyOCR Reader for the required languages (Cyrillic and Latin-based)
                self.reader = easyocr.Reader(
                    ["ru", "rs_cyrillic", "be", "bg", "uk", "mn", "en"], gpu=False  # Disable GPU explicitly
                )

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess the image before performing OCR to enhance text recognition accuracy.
        :param image_path: Path to the image file.
        :return: Preprocessed image in numpy array format.
        """
        image = Image.open(image_path)
        image = image.convert("L")  # Convert to grayscale
        return np.array(image)

        # Perform further preprocessing steps if necessary (e.g., resizing, etc.)
        # Example: image_np = cv2.resize(image_np, (new_width, new_height))

    def extract_text(self) -> str:
        """
        Extract text from the image using EasyOCR.
        :return: Extracted text as a string.
        """
        try:
            image_np = self.preprocess_image(self.file_path)
            results = self.reader.readtext(image_np)
            return "\n".join([result[1] for result in results if result[1]])
        except Exception as e:
            print(f"Error processing image: {e}")
            return ""
    def search(self, keyword: str, exact_match: bool = False) -> list[str]:
        """
        Search for a keyword in text extracted from the image using EasyOCR.
        :param keyword: The keyword to search for.
        :return: A list of lines containing the keyword.
        """

        text = self.extract_text()
        return TextSearcher.search_text(text, keyword, exact_match)

    def read(self) -> str:
        """
        Read the extracted text from the image and return it as a string.
        :return: Extracted text as a string.
        """
        return self.extract_text()
