"""Python script for creating jsonl database"""
import utils
import constants
import os
import json

from dotenv import load_dotenv
import argparse


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
        self._jsonl_dataset_path = jsonl_dataset_path

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

        # Write jsonl_dataset_list to jsonl file
        os.makedirs(
            constants.RootDirectory.JSONL_DATASET_ROOT.value, exist_ok=True)
        with open(os.path.join(self._jsonl_dataset_path, "jsonl_dataset.jsonl"), "w") as file:
            for jsonl in jsonl_dataset_list:
                json.dump(jsonl, file)
                file.write('\n')

        # Log
        print(
            f"JSONL dataset successfully created with size (threshold={repetitive_word_threshold}): {len(jsonl_dataset_list)} records")


if __name__ == "__main__":
    main()
