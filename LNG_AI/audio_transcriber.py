""" Transcribe audio files by AI """
import os

import openai

from LNG_AI import constants


class AudioTranscriber():
    """Transcribe audio files by AI"""

    def __init__(self, mode: constants.TranscribeMode, keys: dict):
        if mode == constants.TranscribeMode.WHISPER:
            if not "openai_api_key" in keys:
                raise KeyError("open_ai_key not exists")
            openai.api_key = keys["openai_api_key"]

        self.mode = mode
        self.key = keys

    def transcribe_dir(self, audio_file_dir: str, is_preview_only: bool):
        """Transcribe eligible mp3 files in the given directory"""
        file_names = os.listdir(audio_file_dir)
        for file_name in file_names:
            file_path = f"{audio_file_dir}/{file_name}"

            # only consider .mp3 files
            ext = os.path.splitext(file_path)[1]
            if ext != ".mp3":
                continue

            preview_condition = constants.AudioFileKeyword.PREVIEW.value in file_name
            five_minutes_chuck_condition = (
                constants.AudioFileKeyword.FIVE_MINUTES_CHUCK.value in file_name) and (not is_preview_only)

            if not (preview_condition or five_minutes_chuck_condition):
                print(f"not applicable file path: {file_path}",
                      f"(is_preview_only={is_preview_only})")
                continue

            self._transcribe_file(file_path)

    def _transcribe_file(self, audio_path: str):
        # Compute output path
        (path_wo_ext, _) = os.path.splitext(audio_path)
        path_items = path_wo_ext.split('/')
        output_txt_dir = "/".join(path_items[:-1]) + "/" + self.mode.value
        output_txt_path = output_txt_dir + "/" + path_items[-1] + ".txt"

        if not os.path.exists(output_txt_dir):
            os.makedirs(output_txt_dir)

        if os.path.isfile(output_txt_path):
            print("ignore transcribe requirement",
                  f", since {output_txt_path} already exists")
            return

        # Transcribe & Parse
        print(f"==> start transcribing {audio_path} to",
              f"{output_txt_path} (not yet exist)")
        if self.mode == constants.TranscribeMode.WHISPER:
            raw_result_str = self._whisper_transribe_file(audio_path)
            self._whisper_parse_and_store_transcribe_result(
                raw_result_str, output_txt_path)

    def _whisper_transribe_file(self, audio_path: str) -> str:
        audio_file = open(audio_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript['text']

    def _whisper_parse_and_store_transcribe_result(
            self, raw_result_str: str, output_txt_path: str):
        with open(output_txt_path, "w", encoding="utf-8") as text_file:
            text_file.write(raw_result_str)
