import re
from abc import ABC, abstractmethod


class FileProcessor(ABC):
    """
    Abstract base class for file processors.
    Each processor must implement the `search` method.
    """

    @abstractmethod
    def search(self, keyword: str, exact_match: bool) -> list[str]:
        """
        Search for a keyword in the file.
        :param keyword: The keyword to search for.
        :param exact_match: All word or friction.
        :return: A list of lines containing the keyword.

        """
        pass
    @abstractmethod
    def read(self) -> str:
        """
        Read the content of the file and return it as a string.
        :return: The content of the file as a string.
        """
        pass

class TextSearcher:
    """
    Utility class for searching keywords in extracted text.
    Handles both exact and partial matches.
    """

    @staticmethod
    def search_text(text: str, keyword: str, exact_match: bool) -> list[str]:
        """
        Search for a keyword in a given text.
        :param text: Text to search within.
        :param keyword: Keyword to search for.
        :param exact_match: Whether to search for an exact match.
        :return: A list of lines containing the keyword.
        """
        if not text.strip():
            return []

        # Нормалізуємо текст: видаляємо зайві пробіли
        text = ' '.join(text.split())  # Заміна кількох пробілів одним
        keyword = keyword.strip()  # Видаляємо зайві пробіли з ключового слова

        print('TextSearcher:', text)

        if exact_match:
            # Використовуємо регулярний вираз для пошуку точного збігу слова
            # \b - межа слова, re.IGNORECASE - не враховує регістр
            pattern = fr'\b{re.escape(keyword)}\b'
            return [line for line in text.splitlines() if re.search(pattern, line, re.IGNORECASE)]
        else:
            print([line for line in text.splitlines() if keyword.lower() in line.lower()])
            # Частковий збіг: перевіряємо, чи входить слово як підрядок
            return [line for line in text.splitlines() if keyword.lower() in line.lower()]