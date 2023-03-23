"""Python script for grabbing latest Youtube video informations"""
import csv
import logging
import os
import requests

from dotenv import load_dotenv
from pydub import AudioSegment
import pytube

import constants


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


class YoutubeAudioFetcher():
    """Fetcher to grab audio files based on latest videos of the given Youtube channel"""

    def __init__(self, api_key):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = api_key

        if not os.path.exists(constants.RAW_3GG_FILE_ROOT):
            os.makedirs(constants.RAW_3GG_FILE_ROOT)

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
        audio_file_dir = f"{constants.AUDIO_FILE_ROOT}/{item['id']}"
        raw_3gg_file_path = f"{constants.RAW_3GG_FILE_ROOT}/{item['id']}.3gg"

        if self._download_audio_file(youtube_video_url, raw_3gg_file_path):
            print(f"Successfully downloaded {item['snippet']['title']}")
            # transfer video to audio & cut audio as well
            self._transfer_raw_to_audio_file(raw_3gg_file_path, audio_file_dir)
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

    def _download_audio_file(self, youtube_video_url: str, raw_3gg_file_path: str) -> bool:
        if os.path.isfile(raw_3gg_file_path):
            print(f"{raw_3gg_file_path} already exists, avoid downloading")
            return True

        # Only download if not exist
        try:
            # known issue: https://github.com/pytube/pytube/issues/1498
            items = raw_3gg_file_path.split('/')
            file_dir, file_name = items[0], items[1]
            _ = pytube.YouTube(youtube_video_url).streams.first().download(
                output_path=file_dir, filename=file_name)
        # lazy to specify exception type(s) for now
        # catch all potential errors
        except:
            return False

        return True

    def _transfer_raw_to_audio_file(self, raw_3gg_file_path: str, audio_file_dir: str):
        if not os.path.exists(audio_file_dir):
            os.makedirs(audio_file_dir)

        # Full audio
        print("processing full audio")
        audio = AudioSegment.from_file(raw_3gg_file_path)
        self._export_if_not_exist(audio, f"{audio_file_dir}/full.mp3")

        # 1-minute preview
        print("processing 1-minute preview audio")
        one_minute_preview_audio = audio[:constants.ONE_MINUTE_IN_MILLISECONDS]
        self._export_if_not_exist(
            one_minute_preview_audio, f"{audio_file_dir}/one_minute_preview.mp3")

        # TODO: below two code snippets (1-hour and 5-miutes are highly similar),
        # should pack in a method if neededgi

        # 1-hour audio chucks
        print("processing audio chucks by hours")
        total_length_in_milliseconds = len(audio)
        one_hour_in_milliseconds = 60 * constants.ONE_MINUTE_IN_MILLISECONDS
        i = 0
        # next hour still not yet finish
        while (i+1) * one_hour_in_milliseconds < total_length_in_milliseconds:
            begin = i * one_hour_in_milliseconds
            end = (i+1) * one_hour_in_milliseconds
            one_hour_chuck_audio = audio[begin:end]
            self._export_if_not_exist(
                one_hour_chuck_audio,  f"{audio_file_dir}/{i+1}_hour_chuck.mp3")
            i += 1

        last_hour_check_audio = audio[i * one_hour_in_milliseconds:]
        self._export_if_not_exist(
            last_hour_check_audio,  f"{audio_file_dir}/{i+1}_hour_chuck.mp3")

        # 5-minutes audio chucks
        print("processing audio chucks per 5 minutes ")
        total_length_in_milliseconds = len(audio)
        five_minutes_in_milliseconds = 5 * constants.ONE_MINUTE_IN_MILLISECONDS
        i = 0
        # next hour still not yet finish
        while (i+1) * five_minutes_in_milliseconds < total_length_in_milliseconds:
            begin = i * five_minutes_in_milliseconds
            end = (i+1) * five_minutes_in_milliseconds
            one_hour_chuck_audio = audio[begin:end]
            self._export_if_not_exist(
                one_hour_chuck_audio,  f"{audio_file_dir}/{i+1}_5_mins_chuck.mp3")
            i += 1

        last_hour_check_audio = audio[i * five_minutes_in_milliseconds:]
        self._export_if_not_exist(
            last_hour_check_audio,  f"{audio_file_dir}/{i+1}_5_mins_chuck.mp3")

    def _export_if_not_exist(self, audio, export_path):
        if os.path.isfile(export_path):
            print(f"{export_path} already exists, avoid exporting")
            return

        print(f"exporting audio to {export_path}")
        audio.export(export_path, format="mp3")


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
