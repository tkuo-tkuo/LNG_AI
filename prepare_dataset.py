"""Python script for creating jsonl database"""
import os
import json

from dotenv import load_dotenv
import argparse

from LNG_AI import utils
from LNG_AI import constants

def main():
    """Create jsonl database"""
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitive_word_threshold", type=float, default=0.1)
    args = parser.parse_args()

    # check valid threshold
    assert args.repetitive_word_threshold >= 0 and args.repetitive_word_threshold <= 1

    load_dotenv()
    jsonl_database_creator = JsonlDatabaseCreator(
        constants.RootDirectory.JSONL_DATASET_ROOT.value)
    jsonl_database_creator.create_jsonl_database(
        repetitive_word_threshold=args.repetitive_word_threshold, debug=False)


class JsonlDatabaseCreator():
    """Class for creating jsonl database"""

    def __init__(self, jsonl_dataset_path: str) -> None:
        pass

    def create_jsonl_database(self, repetitive_word_threshold: float, debug: bool):
        """Create jsonl database"""
        jsonl_dataset_list = []

        # Get list of jsonl
        audio_file_dirs = utils.FileUtils.get_audio_file_directories()
        for audio_file_dir in audio_file_dirs:
            for five_minutes_transcript_path in utils.FileUtils.get_five_minutes_chuck_transcript_paths(audio_file_dir):
                # True means okay (not repetitive)
                if utils.TranscriptUtils.check_transcript_repetitive_word_occurance(five_minutes_transcript_path, repetitive_word_threshold, debug):
                    with open(five_minutes_transcript_path, "r") as file:
                        words = file.read().split(" ")
                        assert len(words) >= 2

                        for idx in range(0, len(words)-1):
                            # Reference: https://platform.openai.com/docs/guides/fine-tuning
                            jsonl = {"prompt": words[idx],
                                     "completion": words[idx+1]}
                            jsonl_dataset_list.append(jsonl)

        # Store a portion of the jsonl_dataset_list
        portions = [0.005, 0.01, 0.1, 0.2, 0.3,
                    0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        for portion in portions:
            utils.JsonlUtils.store_portion_jsonl(
                jsonl_dataset_list, portion)


if __name__ == "__main__":
    main()
