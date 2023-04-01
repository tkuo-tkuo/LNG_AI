"""Python script for creating jsonl database"""
from dotenv import load_dotenv
import argparse

from LNG_AI import utils


def main():
    """Create jsonl database"""
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitive_word_threshold", type=float, default=0.1)
    args = parser.parse_args()

    # check valid threshold
    assert args.repetitive_word_threshold >= 0 and args.repetitive_word_threshold <= 1

    load_dotenv()
    utils.JsonlUtils().create_jsonl_database(
        repetitive_word_threshold=args.repetitive_word_threshold, debug=False)


if __name__ == "__main__":
    main()
