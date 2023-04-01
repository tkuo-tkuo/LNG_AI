"""Python script for grabbing latest Youtube video informations"""
import os

from dotenv import load_dotenv

from LNG_AI import utils
from LNG_AI import youtube_audio_fetecher


def main():
    """Grab audio informations given youtube channel ID & store results"""
    load_dotenv()
    yt_api_key = os.getenv('yt_api_key')
    yt_channel_id = "UCKngQgSGHd3Hp3nkPs15YSA"  # LNG

    lng_audio_fetcher = youtube_audio_fetecher.YoutubeAudioFetcher(yt_api_key)
    num_of_request_results = 10
    audio_infos = lng_audio_fetcher.obtain_audio_infos(
        yt_channel_id, num_of_request_results)

    # helper functions for displaying/storing results
    utils.FileUtils.store_as_html(audio_infos, "audio_infos.md")
    utils.FileUtils.store_as_csv(audio_infos, "audio_infos.csv")


if __name__ == "__main__":
    main()
