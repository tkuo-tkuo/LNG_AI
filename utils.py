"""Python script for common utilities"""
import os

from dotenv import load_dotenv

import constants


class FileUtils():
    """Class for common utilities"""
    @staticmethod
    def get_audio_file_directories() -> list:
        """Get file directories for each episode"""
        audio_file_root = constants.RootDirectory.AUDIO_FILE_ROOT.value
        audio_ids = os.listdir(audio_file_root)
        return [f"{audio_file_root}/{audio_id}" for audio_id in audio_ids]
