"""Python script for checking data integrity"""
import os
import math
import logging

from dotenv import load_dotenv

import constants
import utils

# TODO: upload environment.yml after this script is completed


def record_failure_success(func):
    """decorator for recording failure/success"""
    def wrapper(*args, **kwargs):
        args[0]._total_cnt += 1
        result = func(*args, **kwargs)
        if result:
            args[0]._success_cnt += 1
        else:
            args[0]._failure_cnt += 1
    return wrapper


def main():
    """Check data integrity"""
    load_dotenv()
    data_integrity_checker = DataIntegrityChecker()
    data_integrity_checker.check_audio_files_creation()
    data_integrity_checker.check_transcripts_creation()
    data_integrity_checker.check_transcripts_repetitive_word_occurance()


class DataIntegrityChecker():
    """Class for checking data integrity"""

    def __init__(self) -> None:
        self._init_cnt()

    def _init_cnt(self):
        self._failure_cnt = 0
        self._success_cnt = 0
        self._total_cnt = 0

    @record_failure_success
    def _check_transcript_repetitive_word_occurance(self, transcript_path: str) -> None:
        return utils.TranscriptUtils.check_transcript_repetitive_word_occurance(transcript_path, 0.1, False)

    @record_failure_success
    def _check_file_exist(self, file_path: str) -> None:
        if not os.path.isfile(file_path):
            logging.error(file_path, "is not exist")
            return False

        return True

    def check_transcripts_creation(self) -> None:
        """Check if transcripts are created successfully"""
        audio_file_dirs = utils.FileUtils.get_audio_file_directories()
        for audio_file_dir in audio_file_dirs:
            # 1-minute transcripit preview
            self._check_file_exist(
                f"{audio_file_dir}/whisper/{constants.AudioFileKeyword.PREVIEW.value}.txt")

            # 5-minutes transcripts
            for five_minutes_transcript_path in utils.FileUtils.get_five_minutes_chuck_transcript_paths(audio_file_dir):
                self._check_file_exist(five_minutes_transcript_path)

        print(f"Transcripts created successfully: {100 * self._success_cnt/self._total_cnt}%",
              f"({self._success_cnt}/{self._total_cnt})")
        self._init_cnt()

    def check_transcripts_repetitive_word_occurance(self) -> None:
        """Check if transcripts have not reptitive word occurance"""
        audio_file_dirs = utils.FileUtils.get_audio_file_directories()
        for audio_file_dir in audio_file_dirs:
            # 5-minutes transcripts
            for five_minutes_transcript_path in utils.FileUtils.get_five_minutes_chuck_transcript_paths(audio_file_dir):
                self._check_transcript_repetitive_word_occurance(
                    five_minutes_transcript_path)

        print(f"Transcripts AI-transcribed successfully: {100 * self._success_cnt/self._total_cnt}%",
              f"({self._success_cnt}/{self._total_cnt})")
        self._init_cnt()

    def check_audio_files_creation(self) -> None:
        """Check if audio files are created successfully"""
        audio_file_dirs = utils.FileUtils.get_audio_file_directories()
        for audio_file_dir in audio_file_dirs:
            self._check_file_exist(
                f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")
            self._check_file_exist(
                f"{audio_file_dir}/{constants.AudioFileKeyword.PREVIEW.value}.mp3")

            # 1-hour audios
            for one_hour_audio_path in utils.FileUtils.get_one_hour_chuck_audio_paths(audio_file_dir):
                self._check_file_exist(one_hour_audio_path)

            # 5-minutes audios
            for five_minutes_audio_path in utils.FileUtils.get_five_minutes_chuck_audio_paths(audio_file_dir):
                self._check_file_exist(five_minutes_audio_path)

        print(f"Audio files created successfully: {100 * self._success_cnt/self._total_cnt}%",
              f"({self._success_cnt}/{self._total_cnt})")
        self._init_cnt()


if __name__ == "__main__":
    main()
