"""Python script for creating jsonl database"""
import os

from dotenv import load_dotenv

import constants

def main():
    """Create jsonl database"""
    load_dotenv()
    jsonl_database_creator = JsonlDatabaseCreator()
    jsonl_database_creator.create_jsonl_database()
    print("Done!")

class JsonlDatabaseCreator():
    """Class for creating jsonl database"""

    def __init__(self) -> None:
        pass

    
    def create_jsonl_database(self, jsonl_dataset_path: str):
        """Create jsonl database"""
        # TODO: generate jsonl files based on transcripts into one folder (e.g., jsonl_dataset)


if __name__ == "__main__":
    main()
