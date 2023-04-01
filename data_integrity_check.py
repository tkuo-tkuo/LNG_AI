"""Python script for checking data integrity"""
from dotenv import load_dotenv

from LNG_AI import data_integrity_checker


def main():
    """Check data integrity"""
    load_dotenv()
    checker = data_integrity_checker.DataIntegrityChecker()
    checker.check_audio_files_creation()
    checker.check_transcripts_creation()
    checker.check_transcripts_repetitive_word_occurance()


if __name__ == "__main__":
    main()
