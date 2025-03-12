import speech_recognition as sr
from .base_processor import FileProcessor

class AudioProcessor(FileProcessor):
    """
    Processor for audio files using speech-to-text.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def search(self, keyword: str) -> list[str]:
        """
        Search for a keyword in an audio file (using speech-to-text).
        :param keyword: The keyword to search for in the transcribed text.
        :return: A list of lines (or words) containing the keyword.
        """
        results = []
        try:
            recognizer = sr.Recognizer()

            # Load the audio file
            with sr.AudioFile(self.file_path) as source:
                audio_data = recognizer.record(source)

            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio_data)

            # Search for the keyword in the recognized text
            for line in text.split('.'):  # Split the text into sentences
                if keyword.lower() in line.lower():  # Case-insensitive search
                    results.append(line.strip())  # Add matching lines

        except sr.UnknownValueError:
            return ["Error: Could not understand the audio."]
        except sr.RequestError as e:
            return [f"Error: Could not request results from Google Speech Recognition service; {e}"]
        except Exception as e:
            return [f"Error: {str(e)}"]

        return results

    def read(self) -> str:
        """
        Read the entire recognized text from the audio file.
        :return: The full transcribed text from the audio file.
        """
        try:
            recognizer = sr.Recognizer()

            # Load the audio file
            with sr.AudioFile(self.file_path) as source:
                audio_data = recognizer.record(source)

            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio_data)

            return text.strip()  # Return the full transcribed text

        except sr.UnknownValueError:
            return "Error: Could not understand the audio."
        except sr.RequestError as e:
            return f"Error: Could not request results from Google Speech Recognition service; {e}"
        except Exception as e:
            return f"Error: {str(e)}"
