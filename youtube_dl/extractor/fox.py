# coding: utf-8
from __future__ import unicode_literals

from .adobepass import AdobePassIE
from ..utils import (
    int_or_none,
    parse_age_limit,
    parse_duration,
    try_get,
    unified_timestamp,
)


class FOXIE(AdobePassIE):
    _VALID_URL = r'https?://(?:www\.)?fox\.com/watch/(?P<id>[\da-fA-F]+)'
    _TESTS = [{
        # clip
        'url': 'https://www.fox.com/watch/4b765a60490325103ea69888fb2bd4e8/',
        'md5': 'ebd296fcc41dd4b19f8115d8461a3165',
        'info_dict': {
            'id': '4b765a60490325103ea69888fb2bd4e8',
            'ext': 'mp4',
            'title': 'Aftermath: Bruce Wayne Develops Into The Dark Knight',
            'description': 'md5:549cd9c70d413adb32ce2a779b53b486',
            'duration': 102,
            'timestamp': 1504291893,
            'upload_date': '20170901',
            'creator': 'FOX',
            'series': 'Gotham',
        },
        'params': {
            'skip_download': True,
        },
    }, {
        # episode, geo-restricted
        'url': 'https://www.fox.com/watch/087036ca7f33c8eb79b08152b4dd75c1/',
        'only_matching': True,
    }, {
        # episode, geo-restricted, tv provided required
        'url': 'https://www.fox.com/watch/30056b295fb57f7452aeeb4920bc3024/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        video = self._download_json(
            'https://api.fox.com/fbc-content/v1_4/video/%s' % video_id,
            video_id, headers={
                'apikey': 'abdcbed02c124d393b39e818a4312055',
                'Content-Type': 'application/json',
                'Referer': url,
            })

        title = video['name']

        m3u8_url = self._download_json(
            video['videoRelease']['url'], video_id)['playURL']

        formats = self._extract_m3u8_formats(
            m3u8_url, video_id, 'mp4',
            entry_protocol='m3u8_native', m3u8_id='hls')
        self._sort_formats(formats)

        description = video.get('description')
        duration = int_or_none(video.get('durationInSeconds')) or int_or_none(
            video.get('duration')) or parse_duration(video.get('duration'))
        timestamp = unified_timestamp(video.get('datePublished'))
        age_limit = parse_age_limit(video.get('contentRating'))

        data = try_get(
            video, lambda x: x['trackingData']['properties'], dict) or {}

        creator = data.get('brand') or data.get('network') or video.get('network')

        series = video.get('seriesName') or data.get(
            'seriesName') or data.get('show')
        season_number = int_or_none(video.get('seasonNumber'))
        episode = video.get('name')
        episode_number = int_or_none(video.get('episodeNumber'))
        release_year = int_or_none(video.get('releaseYear'))

        if data.get('authRequired'):
            # TODO: AP
            pass

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'duration': duration,
            'timestamp': timestamp,
            'age_limit': age_limit,
            'creator': creator,
            'series': series,
            'season_number': season_number,
            'episode': episode,
            'episode_number': episode_number,
            'release_year': release_year,
            'formats': formats,
        }
