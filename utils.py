"""Python script for common utilities"""
import os
import math

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
