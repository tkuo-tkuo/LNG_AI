"""Python script for grabbing latest Youtube video informations"""
import csv
import logging
import os
import requests

from dotenv import load_dotenv
from pydub import AudioSegment
import pytube


ONE_MINUTE_IN_MILLISECONDS = 1 * 60 * 1000
ONE_HOUR_IN_MILLISECONDS = 1 * 60 * ONE_MINUTE_IN_MILLISECONDS
AUDIO_FILE_ROOT = "audio_files"


def main():
    """Grab audio informations given youtube channel ID & store results"""
    load_dotenv()
    yt_api_key = os.getenv('yt_api_key')
    yt_channel_id = "UCKngQgSGHd3Hp3nkPs15YSA"  # LNG

    lng_audio_fetcher = YoutubeAudioFetcher(yt_api_key)
    num_of_request_results = 10
    audio_infos = lng_audio_fetcher.obtain_audio_infos(
        yt_channel_id, num_of_request_results)

    # helper functions for displaying/storing results
    store_as_html(audio_infos, "audio_infos.md")
    store_as_csv(audio_infos, "audio_infos.csv")

    # Clean-up potential intermediate .3gpp raw files
    os.system('rm *.3gpp')


class YoutubeAudioFetcher():
    """Fetcher to grab audio files based on latest videos of the given Youtube channel"""

    def __init__(self, api_key):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = api_key

    def obtain_audio_infos(self, channel_id: str, num_of_request_results: int):
        """Fetches (maximum 50) audios informations frrom latest videos given a channel ID

        Note: maximum 50 videos per query (restricted by youtube API) 

        Args:
            channel_id: channel ID of the youtube channel

        Returns:
            A list of dict, where contains information of a video 
            For instance: {'id':..., 'title':..., 'publishedAt':..., 
                           'audio_source_url':..., 'audio_file_path':...}
        """
        uploads_id = self._get_uploads_id(channel_id)
        video_ids = self._get_video_ids(uploads_id, num_of_request_results)

        return [self._get_audio(video_id) for video_id in video_ids]

    def _get_uploads_id(self, channel_id: str):
        query_url = self._construct_channels_api_query_url(channel_id)
        resp_json = self._send_query(query_url)
        uploads_id = self._parse_channels_api_response(resp_json)
        return uploads_id

    def _get_video_ids(self, uploads_id: str, num_of_request_results: int):
        query_url = self.__construct_playlistitems_api_query_url(
            uploads_id, num_of_request_results)
        resp_json = self._send_query(query_url)
        video_ids = self._parse_playlistitems_api_response(resp_json)
        return video_ids

    def _get_audio(self, video_id: str):
        query_url = self.__construct_videos_api_query_url(video_id)
        resp_json = self._send_query(query_url)
        audio_info = self._parse_videos_api_response_and_download_audio(
            resp_json)
        return audio_info

    # Reference: https://developers.google.com/youtube/v3/docs/channels
    def _construct_channels_api_query_url(self, channel_id: str):
        query_path = f'part=contentDetails&id={channel_id}&maxResults=50'
        query_url = f'{self.base_url}/channels?key={self.api_key}&{query_path}'
        return query_url

    # Reference: https://developers.google.com/youtube/v3/docs/playlistItems
    def __construct_playlistitems_api_query_url(self, uploads_id: str, num_of_request_results: int):
        query_path = f'part=contentDetails&playlistId={uploads_id}&maxResults={num_of_request_results}'
        query_url = f'{self.base_url}/playlistItems?key={self.api_key}&{query_path}'
        return query_url

    # Reference: https://developers.google.com/youtube/v3/docs/videos
    def __construct_videos_api_query_url(self, video_id: str):
        query_path = f'part=snippet&id={video_id}'
        query_url = f'{self.base_url}/videos?key={self.api_key}&{query_path}'
        return query_url

    def _send_query(self, query_url: str):
        resp = requests.get(query_url, timeout=5)
        return resp.json() if resp.status_code == requests.codes['ok'] else None

    def _parse_channels_api_response(self, resp_json):
        uploads_id = None
        try:
            uploads_id = resp_json['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        except KeyError:
            logging.error('can not locate uploads ID')
        return uploads_id

    def _parse_playlistitems_api_response(self, resp_json):
        return [item['contentDetails']['videoId'] for item in resp_json['items']]

    def _parse_videos_api_response_and_download_audio(self, resp_json):
        item = resp_json['items'][0]
        youtube_video_url = f"https://www.youtube.com/watch?v={item['id']}"
        audio_file_dir = f"{AUDIO_FILE_ROOT}/{item['id']}"

        raw_output_file_path = self._download_audio_file(youtube_video_url)

        if raw_output_file_path:
            print(f"Successfully downloaded {item['snippet']['title']}")
            # transfer video to audio & cut audio as well
            self._transfer_raw_to_audio_file(
                raw_output_file_path, audio_file_dir)
        else:
            print(
                f"Something wrong while downloading {item['snippet']['title']}")
            audio_file_dir = ''

        audio_info = {
            'id': item['id'],
            'title': item['snippet']['title'],
            'publishedAt': item['snippet']['publishedAt'],
            'audio_source_url': youtube_video_url,
            'audio_file_dir': audio_file_dir,
        }
        return audio_info

    def _download_audio_file(self, youtube_video_url: str) -> str:
        try:
            output_file_path = pytube.YouTube(
                youtube_video_url).streams.first().download()
            return output_file_path
        # lazy to specify exception type(s) for now
        # catch all potential errors
        except:
            return ""

    def _transfer_raw_to_audio_file(self, raw_output_file_path: str, audio_file_dir: str):
        if not os.path.exists(audio_file_dir):
            os.makedirs(audio_file_dir)

        # Full audio
        print("processing full audio")
        audio = AudioSegment.from_file(raw_output_file_path)
        audio.export(f"{audio_file_dir}/full.mp3", format="mp3")

        # 1-minute preview
        print("processing 1-minute preview audio")
        one_minute_preview_audio = audio[:ONE_MINUTE_IN_MILLISECONDS]
        one_minute_preview_audio.export(
            f"{audio_file_dir}/one_minute_preview.mp3", format="mp3")

        # Due to the limitation of Whisper API, we need to divide audio files (max 25M)
        # Hence, we'll split full audio into 1-hour audio chucks
        print("processing audio chucks by hours")
        total_length_in_milliseconds = len(audio)
        i = 0
        # next hour still not yet finish
        while (i+1) * ONE_HOUR_IN_MILLISECONDS < total_length_in_milliseconds:
            begin = i * ONE_HOUR_IN_MILLISECONDS
            end = (i+1) * ONE_HOUR_IN_MILLISECONDS
            one_hour_chuck_audio = audio[begin:end]
            one_hour_chuck_audio.export(
                f"{audio_file_dir}/{i+1}_hour_chuck.mp3", format="mp3")
            i += 1

        last_hour_check_audio = audio[i * ONE_HOUR_IN_MILLISECONDS:]
        last_hour_check_audio.export(
            f"{audio_file_dir}/{i+1}_hour_chuck.mp3", format="mp3")


def store_as_html(video_infos, store_file_path):
    '''helper function to store latest video infos in md file'''
    with open(store_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(
            '| Title | Audio Dir | Published at | ID | Source URL |\n')
        html_file.write('| ------ | ------ | --- | --- | ------ |\n')
        # TODO: add relative links for audio files
        for video_info in video_infos:
            html_file.write(
                f'| {video_info["title"]} | {video_info["audio_file_dir"]} '
                f'| {video_info["publishedAt"]} | {video_info["id"]} '
                f'| {video_info["audio_source_url"]} |\n')


def store_as_csv(video_infos, store_file_path):
    '''helper function to store latest video infos in csv file'''
    with open(store_file_path, "w", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Title", "Audio Dir",
                            "Published at", "ID", "Source URL"])

        rows = [[video_info["title"], video_info["audio_file_dir"], video_info["publishedAt"],
                 video_info["id"], video_info["audio_source_url"]] for video_info in video_infos]
        csv_writer.writerows(rows)


if __name__ == "__main__":
    main()