"""Python script for transcribe downloaded Youtube audio files"""
import os

from dotenv import load_dotenv

from LNG_AI import constants
from LNG_AI import audio_transcriber


def main():
    """Grab audio informations given youtube channel ID & store results"""
    load_dotenv()

    keys = {"openai_api_key": os.getenv("OPENAI_API_KEY")}
    transcriber = audio_transcriber.AudioTranscriber(
        constants.TranscribeMode.WHISPER, keys)

    is_preview_only = False
    audio_file_root = constants.RootDirectory.AUDIO_FILE_ROOT.value
    audio_ids = os.listdir(audio_file_root)
    for audio_id in audio_ids:
        audio_file_dir = f"{audio_file_root}/{audio_id}"
        transcriber.transcribe_dir(audio_file_dir, is_preview_only)


if __name__ == "__main__":
    main()
