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
    load_dotenv()
    check_audio_files()
    check_transcripts()


def check_transcripts():
    # TODO: later make success_cnt, failure_cnt a class private variable
    failure_cnt, success_cnt = 0, 0

    audio_ids = os.listdir(constants.AUDIO_FILE_ROOT)
    for audio_id in audio_ids:
        audio_file_dir = f"{constants.AUDIO_FILE_ROOT}/{audio_id}"

        # 1-minute transcripit preview
        if _check_file_exist(
                f"{audio_file_dir}/whisper/{constants.AudioFileKeyword.PREVIEW.value}.txt"):
            success_cnt += 1
        else:
            failure_cnt += 1

        # 5-minutes transcripts
        total_length_in_milliseconds = _get_audio_length_in_milliseconds(
            f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")
        five_minutes_in_milliseconds = 5 * constants.ONE_MINUTE_IN_MILLISECONDS
        upper_bound_index_hourly_chuck = math.ceil(
            total_length_in_milliseconds/five_minutes_in_milliseconds)
        for idx in range(1, upper_bound_index_hourly_chuck+1):
            if _check_file_exist(
                    f"{audio_file_dir}/whisper/{idx}{constants.AudioFileKeyword.FIVE_MINUTES_CHUCK.value}.txt"):
                success_cnt += 1
            else:
                failure_cnt += 1

    total_cnt = success_cnt + failure_cnt
    print(
        f"Transcripts created successfully: {100 * success_cnt/total_cnt}% ({success_cnt}/{total_cnt})")


def check_audio_files():
    failure_cnt, success_cnt = 0, 0

    audio_ids = os.listdir(constants.AUDIO_FILE_ROOT)
    for audio_id in audio_ids:
        audio_file_dir = f"{constants.AUDIO_FILE_ROOT}/{audio_id}"

        if _check_file_exist(
                f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3"):
            success_cnt += 1
        else:
            failure_cnt += 1

        if _check_file_exist(
                f"{audio_file_dir}/{constants.AudioFileKeyword.PREVIEW.value}.mp3"):
            success_cnt += 1
        else:
            failure_cnt += 1

        total_length_in_milliseconds = _get_audio_length_in_milliseconds(
            f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")

        # 1-hour audio chuck check
        one_hour_in_milliseconds = 60 * constants.ONE_MINUTE_IN_MILLISECONDS
        upper_bound_index_hourly_chuck = math.ceil(
            total_length_in_milliseconds/one_hour_in_milliseconds)
        for idx in range(1, upper_bound_index_hourly_chuck+1):
            if _check_file_exist(
                    f"{audio_file_dir}/{idx}{constants.AudioFileKeyword.HOUR_CHUCK.value}.mp3"):
                success_cnt += 1
            else:
                failure_cnt += 1
        # 5-minutes audio chuck check
        five_minutes_in_milliseconds = 5 * constants.ONE_MINUTE_IN_MILLISECONDS
        upper_bound_index_hourly_chuck = math.ceil(
            total_length_in_milliseconds/five_minutes_in_milliseconds)
        for idx in range(1, upper_bound_index_hourly_chuck+1):
            if _check_file_exist(
                    f"{audio_file_dir}/{idx}{constants.AudioFileKeyword.FIVE_MINUTES_CHUCK.value}.mp3"):
                success_cnt += 1
            else:
                failure_cnt += 1

    total_cnt = success_cnt + failure_cnt
    print(
        f"Audio files created successfully: {100 * success_cnt/total_cnt}% ({success_cnt}/{total_cnt})")


def _check_file_exist(file_path: str) -> bool:
    if not os.path.isfile(file_path):
        # continue even one file not exist
        logging.error(f"{file_path} is not exist")
        return False

    return True


def _get_audio_length_in_milliseconds(file_path: str):
    """
    Note: use mutagen.mp3 instead of AudioSegment, which has much lower loading time
    """
    audio = MP3(file_path)
    return audio.info.length * 1000


if __name__ == "__main__":
    main()
