"""Python script for checking data integrity"""


from dotenv import load_dotenv

# TODO: add detection mechanism to avoid suspicious txt (repetitive word occurance)
# TODO: check audio & transcript data integrity
# TODO: generate jsonl files based on transcripts into one folder


def main():
    load_dotenv()

    # TODO: add detection mechanism to avoid suspicious txt (repetitive word occurance)
    # 1. for loop to locate every transcript in audio_files/
    # 2. for every transcript, translate as list 

if __name__ == "__main__":
    main()
