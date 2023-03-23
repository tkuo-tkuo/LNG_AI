"""Python script for checking data integrity"""
import os
import math

from dotenv import load_dotenv
from mutagen.mp3 import MP3

import constants

# TODO: add detection mechanism to avoid suspicious txt (repetitive word occurance)
# TODO: check audio & transcript data integrity
# TODO: generate jsonl files based on transcripts into one folder
# TODO: upload environment.yml after this script is completed


def main():
    load_dotenv()

    # TODO: add detection mechanism to avoid suspicious txt (repetitive word occurance)
    # 1. for loop to locate every transcript in audio_files/
    # 2. for every transcript, translate as list

    # TODO: check transcript

    # check audio files
    check_audio_files()


def check_audio_files():
    audio_ids = os.listdir(constants.AUDIO_FILE_ROOT)
    for audio_id in audio_ids:
        audio_file_dir = f"{constants.AUDIO_FILE_ROOT}/{audio_id}"

        _check_file_exist(
            f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")
        _check_file_exist(
            f"{audio_file_dir}/{constants.AudioFileKeyword.PREVIEW.value}.mp3")

        total_length_in_milliseconds = _get_audio_length_in_milliseconds(
            f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")

        # 1-hour audio chuck check
        one_hour_in_milliseconds = 60 * constants.ONE_MINUTE_IN_MILLISECONDS
        upper_bound_index_hourly_chuck = math.ceil(
            total_length_in_milliseconds/one_hour_in_milliseconds)
        for idx in range(1, upper_bound_index_hourly_chuck+1):
            _check_file_exist(
                f"{audio_file_dir}/{idx}{constants.AudioFileKeyword.HOUR_CHUCK.value}.mp3")

        # 5-minutes audio chuck check
        five_minutes_in_milliseconds = 5 * constants.ONE_MINUTE_IN_MILLISECONDS
        upper_bound_index_hourly_chuck = math.ceil(
            total_length_in_milliseconds/five_minutes_in_milliseconds)
        for idx in range(1, upper_bound_index_hourly_chuck+1):
            _check_file_exist(
                f"{audio_file_dir}/{idx}{constants.AudioFileKeyword.FIVE_MINUTES_CHUCK.value}.mp3")


def _check_file_exist(file_path: str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} is not exist")


def _get_audio_length_in_milliseconds(file_path: str):
    """
    Note: use mutagen.mp3 instead of AudioSegment, which has much lower loading time
    """
    audio = MP3(file_path)
    return audio.info.length * 1000


if __name__ == "__main__":
    main()
