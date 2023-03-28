"""Python script for common utilities"""
import os
import math
import logging
import random
import json
from collections import Counter

from dotenv import load_dotenv
from mutagen.mp3 import MP3

import constants

# TODO: use Google style linting


class FileUtils():
    """Class for common file utilities"""
    @staticmethod
    def get_audio_file_directories() -> list:
        """Get file directories for each episode"""
        audio_file_root = constants.RootDirectory.AUDIO_FILE_ROOT.value
        audio_ids = os.listdir(audio_file_root)
        return [f"{audio_file_root}/{audio_id}" for audio_id in audio_ids]

    @staticmethod
    def get_one_hour_chuck_audio_paths(audio_file_dir: str) -> list:
        """Get five minutes chuck audios"""
        return FileUtils.get_five_minutes_chuck_paths(audio_file_dir,
                                                      chuck_keyword=constants.AudioFileKeyword.HOUR_CHUCK,
                                                      ext_type="audio")

    @staticmethod
    def get_five_minutes_chuck_audio_paths(audio_file_dir: str) -> list:
        """Get five minutes chuck audios"""
        return FileUtils.get_five_minutes_chuck_paths(audio_file_dir,
                                                      chuck_keyword=constants.AudioFileKeyword.FIVE_MINUTES_CHUCK,
                                                      ext_type="audio")

    @staticmethod
    def get_five_minutes_chuck_transcript_paths(audio_file_dir: str) -> list:
        """Get five minutes chuck transcripts"""
        return FileUtils.get_five_minutes_chuck_paths(audio_file_dir,
                                                      chuck_keyword=constants.AudioFileKeyword.FIVE_MINUTES_CHUCK,
                                                      ext_type="transcript")

    @staticmethod
    def get_five_minutes_chuck_paths(audio_file_dir: str, chuck_keyword: constants.AudioFileKeyword, ext_type: str) -> list:
        """Get five minutes chuck"""
        # only five-minutes and 1-hour chuck are supported
        if chuck_keyword not in [constants.AudioFileKeyword.FIVE_MINUTES_CHUCK, constants.AudioFileKeyword.HOUR_CHUCK]:
            raise ValueError(f"Invalid chuck_keyword: {chuck_keyword}")

        # Get the total length of the audio file
        total_length_in_milliseconds = AudioUtils.get_audio_length_in_milliseconds(
            f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")

        # Get the upper bound index
        chuck_in_milliseconds = 5 * constants.ONE_MINUTE_IN_MILLISECONDS if chuck_keyword == constants.AudioFileKeyword.FIVE_MINUTES_CHUCK else 60 * \
            constants.ONE_MINUTE_IN_MILLISECONDS
        upper_bound_index = math.ceil(
            total_length_in_milliseconds/chuck_in_milliseconds)

        # Return list
        paths = []
        for idx in range(1, upper_bound_index+1):
            if ext_type == "audio":
                path = f"{audio_file_dir}/{idx}{chuck_keyword.value}.mp3"
            elif ext_type == "transcript":
                path = f"{audio_file_dir}/whisper/{idx}{chuck_keyword.value}.txt"
            else:
                raise ValueError(f"Invalid ext_type: {ext_type}")
            paths.append(path)
        return paths


class AudioUtils():
    """Class for common audio utilities"""
    @staticmethod
    def get_audio_length_in_milliseconds(file_path: str) -> int:
        """
        Note: use mutagen.mp3 instead of AudioSegment, which has much lower loading time
        """
        audio = MP3(file_path)
        return audio.info.length * 1000


class TranscriptUtils():
    """Class for common transcript utilities"""
    @staticmethod
    def check_transcript_repetitive_word_occurance(transcript_path: str, threshold: float, log_error: bool) -> bool:
        """Check if there is any repetitive word in the transcript"""
        assert threshold >= 0 and threshold <= 1, "threshold should be between 0 and 1"

        with open(transcript_path, "r") as file:
            transcript = file.read()
            words = transcript.split(" ")
            words_occurance = Counter(words)

            # check if any word has more than 10% occurance
            # make this part of logic as a util function in utils.py
            total_word_cnt = len(words)
            for word in words_occurance:
                num_of_occurance = words_occurance[word]
                occurance_percentage = round(
                    100 * num_of_occurance/total_word_cnt, 2)
                if occurance_percentage > (threshold * 100):
                    if log_error:
                        error_str = f"{transcript_path} has repetitive word occurance: {word} ({occurance_percentage}%))"
                        logging.error(error_str)
                    return False

        return True


class JsonlUtils():
    """Class for common jsonl utilities"""
    @staticmethod
    def store_portion_jsonl(jsonls: list[dict],  portion: float):
        """Store a portion of the jsonls"""
        assert portion > 0 and portion <= 1, "portion should be between 0 and 1"

        # Get the number of jsonls to store
        num_of_jsonls_to_store = math.ceil(len(jsonls) * portion)

        # Sort the jsonls randomly
        random.shuffle(jsonls)

        # Save the jsonls to export_jsonl_path
        os.makedirs(constants.RootDirectory.JSONL_DATASET_ROOT.value, exist_ok=True)
        export_json_file = f"jsonl_dataset_{int(portion * 100)}_percent_{num_of_jsonls_to_store}.jsonl"
        export_jsonl_path = os.path.join(
            constants.RootDirectory.JSONL_DATASET_ROOT.value, export_json_file)
        with open(export_jsonl_path, "w") as file:
            for idx in range(num_of_jsonls_to_store):
                jsonl = jsonls[idx]
                json.dump(jsonl, file)
                file.write('\n')

            # Log
            print(f"JSONL dataset successfully created with size (portion={portion}): "
                  f"{num_of_jsonls_to_store} records")
