from collections.abc import Callable
from multiprocessing import Pool
from multiprocessing.pool import AsyncResult
from typing import List
import whisper


# TODO: Add per-file progress tracking.
class Transcriber:
    model = None
    completed_files: List[str] = []
    requested_files: List[str] = []

    def __init__(self, whisper_model: str = "base.en"):
        try:
            self.model = whisper.load_model(whisper_model)
        except Exception as e:
            print(f"Error loading Whisper model {whisper_model}: {e}")

    def transcribe(self, filename: str) -> str:
        """Transcribe a single audio file from the given filename.

        Args:
            filename (str): The path to the audio file.

        Returns:
            str: The full transcribed text.
        """
        try:
            self.requested_files.append(filename)
            transcription = self.model.transcribe(filename)
            self.completed_files.append(filename)
        except Exception as e:
            print(f"Error while transcribing a single file {filename}: {e}")
        else:
            return transcription

    def transcribe_many(
        self,
        filenames: List[str],
        callback: Callable[[str], None],
        num_processes: int = 4
    ) -> AsyncResult:
        """Transcribes many audio files in parallel, passing each transcription to the callback
        function as it finishes.

        Args:
            filenames (List[str]): A list of filepaths to audio files.
            callback (Callable[[str], None]): The function to be executed when a transcription is
            finished. Should accept a single string containing the full transcript.
            num_processes (int, optional): The max number of processes to run simultaneously.
            Defaults to 4.

        Returns:
            AsyncResult: Indicates when all the input files have been transcribed.
        """
        def on_error(e: BaseException):
            print(f"Error while transcribing multiple files: {e}")

        with Pool(num_processes) as pool:
            return pool.apply_async(
                self.transcribe,
                args = filenames,
                callback = callback,
                error_callback = on_error
            )
