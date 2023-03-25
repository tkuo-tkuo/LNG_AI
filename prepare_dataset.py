"""Python script for checking data integrity"""
import os
import math
import logging

from dotenv import load_dotenv
from mutagen.mp3 import MP3

import constants

# TODO: add detection mechanism to avoid suspicious txt (repetitive word occurance)
# TODO: generate jsonl files based on transcripts into one folder
# TODO: upload environment.yml after this script is completed


def main():
    """Check data integrity"""
    load_dotenv()
    data_integrity_check = DataIntegrityChecker()
    data_integrity_check.check_audio_files_creation()
    data_integrity_check.check_transcripts_creation()


class DataIntegrityChecker():
    """Class for checking data integrity"""

    def __init__(self) -> None:
        self._init_cnt()

    def _init_cnt(self):
        self._failure_cnt = 0
        self._success_cnt = 0
        self._total_cnt = 0

    def _check_file_exist(self, file_path: str) -> None:
        self._total_cnt += 1

        if not os.path.isfile(file_path):
            logging.error(file_path, "is not exist")
            self._failure_cnt += 1
        else:
            self._success_cnt += 1

    def _get_audio_length_in_milliseconds(self, file_path: str) -> None:
        """
        Note: use mutagen.mp3 instead of AudioSegment, which has much lower loading time
        """
        audio = MP3(file_path)
        return audio.info.length * 1000

    def check_transcripts_creation(self) -> None:
        """Check if transcripts are created successfully"""
        audio_ids = os.listdir(constants.AUDIO_FILE_ROOT)
        for audio_id in audio_ids:
            audio_file_dir = f"{constants.AUDIO_FILE_ROOT}/{audio_id}"

            # 1-minute transcripit preview
            self._check_file_exist(
                f"{audio_file_dir}/whisper/{constants.AudioFileKeyword.PREVIEW.value}.txt")

            # 5-minutes transcripts
            total_length_in_milliseconds = self._get_audio_length_in_milliseconds(
                f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")
            five_minutes_in_milliseconds = 5 * constants.ONE_MINUTE_IN_MILLISECONDS
            upper_bound_index_hourly_chuck = math.ceil(
                total_length_in_milliseconds/five_minutes_in_milliseconds)
            for idx in range(1, upper_bound_index_hourly_chuck+1):
                self._check_file_exist(f"{audio_file_dir}/whisper/{idx}"
                                       f"{constants.AudioFileKeyword.FIVE_MINUTES_CHUCK.value}.txt")

        print(f"Transcripts created successfully: {100 * self._success_cnt/self._total_cnt}%",
              f"({self._success_cnt}/{self._total_cnt})")
        self._init_cnt()

    def check_audio_files_creation(self) -> None:
        """Check if audio files are created successfully"""

        audio_ids = os.listdir(constants.AUDIO_FILE_ROOT)
        for audio_id in audio_ids:
            audio_file_dir = f"{constants.AUDIO_FILE_ROOT}/{audio_id}"

            self._check_file_exist(
                f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")

            self._check_file_exist(
                f"{audio_file_dir}/{constants.AudioFileKeyword.PREVIEW.value}.mp3")

            total_length_in_milliseconds = self._get_audio_length_in_milliseconds(
                f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")

            # 1-hour audio chuck check
            one_hour_in_milliseconds = 60 * constants.ONE_MINUTE_IN_MILLISECONDS
            upper_bound_index_hourly_chuck = math.ceil(
                total_length_in_milliseconds/one_hour_in_milliseconds)
            for idx in range(1, upper_bound_index_hourly_chuck+1):
                self._check_file_exist(
                    f"{audio_file_dir}/{idx}{constants.AudioFileKeyword.HOUR_CHUCK.value}.mp3")

            # 5-minutes audio chuck check
            five_minutes_in_milliseconds = 5 * constants.ONE_MINUTE_IN_MILLISECONDS
            upper_bound_index_hourly_chuck = math.ceil(
                total_length_in_milliseconds/five_minutes_in_milliseconds)
            for idx in range(1, upper_bound_index_hourly_chuck+1):
                self._check_file_exist(f"{audio_file_dir}/{idx}"
                                       f"{constants.AudioFileKeyword.FIVE_MINUTES_CHUCK.value}.mp3")

        print(f"Audio files created successfully: {100 * self._success_cnt/self._total_cnt}%",
              f"({self._success_cnt}/{self._total_cnt})")
        self._init_cnt()


if __name__ == "__main__":
    main()
