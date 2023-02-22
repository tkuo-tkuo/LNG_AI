"""Python script for grabbing latest Youtube video informations"""
import csv
import logging
import requests


YT_API_KEY = "PLACE YOUR GOOGLE CLOUD YOUTUBE API KEY HERE"


def main():
    """Grab video informations given youtube channel ID & store results"""
    yt_channel_id = "UCKngQgSGHd3Hp3nkPs15YSA"  # LNG

    yt_info_fetcher = YoutubeInfoFetcher(YT_API_KEY)
    video_infos = yt_info_fetcher.obtain_video_infos(yt_channel_id)

    # helper functions for displaying/storing results
    store_as_html(video_infos, "latest_video_infos.md")
    store_as_csv(video_infos, "latest_video_infos.csv")


class YoutubeInfoFetcher():
    """Fetcher class for grabbing latest video informations (title/ID/publish date/URL)"""

    def __init__(self, api_key):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = api_key

    def obtain_video_infos(self, channel_id: str):
        """Fetches (maximum 50) video informations given a channel ID

        Maximum 50 video is restricted by youtube API 

        Args:
            channel_id: channel ID of the youtube channel

        Returns:
            A list of dict, where contains information of a video 
            For instance: {'id': ..., 'title': ..., 'publishedAt': ..., 'video_url': ...}
        """
        uploads_id = self._get_uploads_id(channel_id)
        video_ids = self._get_video_ids(uploads_id)

        return [self._get_video(video_id) for video_id in video_ids]

    def _get_uploads_id(self, channel_id: str):
        query_url = self._construct_channels_api_query_url(channel_id)
        resp_json = self._send_query(query_url)
        uploads_id = self._parse_channels_api_response(resp_json)
        return uploads_id

    def _get_video_ids(self, uploads_id):
        query_url = self.__construct_playlistitems_api_query_url(uploads_id)
        resp_json = self._send_query(query_url)
        video_ids = self._parse_playlistitems_api_response(resp_json)
        return video_ids

    def _get_video(self, video_id: str):
        query_url = self.__construct_videos_api_query_url(video_id)
        resp_json = self._send_query(query_url)
        video_info = self._parse_videos_api_response(resp_json)
        return video_info

    # Reference: https://developers.google.com/youtube/v3/docs/channels
    def _construct_channels_api_query_url(self, channel_id: str):
        query_path = f'part=contentDetails&id={channel_id}&maxResults=50'
        query_url = f'{self.base_url}/channels?key={self.api_key}&{query_path}'
        return query_url

    # Reference: https://developers.google.com/youtube/v3/docs/playlistItems
    def __construct_playlistitems_api_query_url(self, uploads_id: str):
        query_path = f'part=contentDetails&playlistId={uploads_id}&maxResults=50'
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

    def _parse_videos_api_response(self, resp_json):
        item = resp_json['items'][0]
        video_info = {
            'id': item['id'],
            'title': item['snippet']['title'],
            'publishedAt': item['snippet']['publishedAt'],
            'video_url': f"https://www.youtube.com/watch?v={item['id']}",
        }
        return video_info


def store_as_html(video_infos, store_file_path):
    '''helper function to store latest video infos in md file'''
    with open(store_file_path, "w", encoding="utf-8") as html_file:
        html_file.write('| Title | Published at | ID | URL |\n')
        html_file.write('| ------ | --- | --- | ------ |\n')
        for video_info in video_infos:
            html_file.write(
                f'| {video_info["title"]} | {video_info["publishedAt"]} '
                '| {video_info["id"]} | {video_info["video_url"]} |\n')


def store_as_csv(video_infos, store_file_path):
    '''helper function to store latest video infos in csv file'''
    with open(store_file_path, "w", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Title", "Published at", "ID", "URL"])

        rows = [[video_info["title"], video_info["publishedAt"], video_info["id"],
                 video_info["video_url"]] for video_info in video_infos]
        csv_writer.writerows(rows)


if __name__ == "__main__":
    main()
