import PyPDF2

from app.file_processors.base_processor import FileProcessor

class PDFProcessor(FileProcessor):
    """
    Processor for PDF files.
    This class provides functionality to search for keywords and read the entire text from a PDF file.
    """

    def __init__(self, file_path: str):
        """
        Initialize the PDF processor with the file path.
        :param file_path: Path to the PDF file.
        """
        self.file_path = file_path

    def search(self, keyword: str, exact_match: bool = True) -> list[str]:
        """
        Search for a keyword in the PDF file and return a list of lines containing the keyword.
        :param keyword: The keyword to search for in the PDF file.
        :param exact_match: _
        :return: A list of lines containing the keyword.
        """
        results = []
        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # Iterate through each page of the PDF
            for page in reader.pages:
                text = page.extract_text()  # Extract text from the page
                if text:  # Check if the page contains text
                    # Split text into lines and check if the keyword exists in each line
                    results.extend([line for line in text.splitlines() if keyword in line])
        return results

    def read(self) -> str:
        """
        Read the entire content of the PDF file and return it as a single string.
        :return: The text content of the entire PDF file.
        """
        full_text = ""
        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # Iterate through each page of the PDF and extract the text
            for page in reader.pages:
                text = page.extract_text()
                if text:  # Only append if text is found on the page
                    full_text += text + "\n"  # Append extracted text, separated by newlines
        return full_text


