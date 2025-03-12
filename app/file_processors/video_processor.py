# import speech_recognition as sr
# from moviepy.editor import AudioFileClip
# from file_processors.base_processor import FileProcessor
#
#
# class VideoProcessor(FileProcessor):
#     """
#     Processor for video files using speech-to-text.
#     """
#     def __init__(self, file_path: str):
#         self.file_path = file_path
#
#     def search(self, keyword: str) -> list[str]:
#         """
#         Extract audio from video and search for a keyword using speech-to-text.
#         """
#         audio_clip = AudioFileClip(self.file_path)
#         temp_audio = "temp_audio.wav"
#         audio_clip.write_audiofile(temp_audio)
#
#         recognizer = sr.Recognizer()
#         results = []
#         with sr.AudioFile(temp_audio) as source:
#             audio_data = recognizer.record(source)
#             text = recognizer.recognize_google(audio_data)
#             results.extend([line for line in text.splitlines() if keyword in line])
#
#         return results
