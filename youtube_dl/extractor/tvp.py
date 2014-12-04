# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from .common import InfoExtractor


class TvpIE(InfoExtractor):
    IE_NAME = 'tvp.pl'
    _VALID_URL = r'https?://(?P<type>vod|www)\.tvp\.pl/.*/(?P<id>\d+)$'

    _TESTS = [
        {
            'url': 'http://www.tvp.pl/warszawa/magazyny/campusnews/wideo/31102013/12878238',
            'info_dict': {
                'id': '12878238',
                'ext': 'wmv',
                'title': 'CAMPUSnews, 31.10.2013 - Odcinek 2',
                'description': '',
            },
            'skip': 'Download has to use same server IP as extraction. Therefore, a good (load-balancing) DNS resolver will make the download fail.',
        }, {
            'url': 'http://vod.tvp.pl/filmy-fabularne/filmy-za-darmo/ogniem-i-mieczem/wideo/odc-2/4278035',
            'info_dict': {
                'id': '4278035',
                'ext': 'wmv',
                'title': 'Ogniem i mieczem, odc. 2',
                'description': 'Bohun dowiaduje się o złamaniu przez kniahinię danego mu słowa i wyrusza do Rozłogów. Helenie w ostatniej chwili udaje się uciec dzięki pomocy Zagłoby.',
            },
            'skip': 'As above',
        }, {
            'url': 'http://vod.tvp.pl/seriale/obyczajowe/czas-honoru/sezon-1-1-13/i-seria-odc-13/194536',
            'info_dict': {
                'id': '194536',
                'ext': 'mp4',
                'title': 'Czas honoru, I seria – odc. 13',
                'description': 'WŁADEK\nCzesław prosi Marię o dostarczenie Władkowi zarazki tyfusu. Jeśli zachoruje zostanie przewieziony do szpitala skąd łatwiej będzie go odbić. Czy matka zdecyduje się zarazić syna? Karol odwiedza Wandę przyznaje się, że ją oszukiwał, ale ostrzega też, że grozi jej aresztowanie i nalega, żeby wyjechała z Warszawy. Czy dziewczyna zdecyduje się znów oddalić od ukochanego? Rozpoczyna się akcja odbicia Władka.',
            },
        }, {
            'url': 'http://www.tvp.pl/there-can-be-anything-so-i-shortened-it/17916176',
            'info_dict': {
                'id': '17916176',
                'ext': 'mp4',
                'title': 'rozmaitosci, TVP Gorzów pokaże filmy studentów z podroży dookoła świata',
                'description': '',
            },
            'params': {
                # m3u8 download
                'skip_download': 'true',
            },
        }, {
            'url': 'http://vod.tvp.pl/seriale/obyczajowe/na-sygnale/sezon-2-27-/odc-39/17834272',
            'info_dict': {
                'id': '17834272',
                'ext': 'mp4',
                'title': 'Na sygnale, odc. 39',
                'description': 'Ekipa Wiktora ratuje młodą matkę, która spadła ze schodów trzymając na rękach noworodka. Okazuje się, że dziewczyna jest surogatką, a biologiczni rodzice dziecka próbują zmusić ją do oddania synka…',
            },
            'params': {
                # m3u8 download
                'skip_download': 'true',
            },
        },
    ]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        webpage = self._download_webpage(
            'http://www.tvp.pl/sess/tvplayer.php?object_id=%s' % video_id, video_id)
        title = self._og_search_title(webpage)
        series = self._search_regex(
            r'{name:\s*([\'"])SeriesTitle\1,\s*value:\s*\1(?P<series>.*?)\1},',
            webpage, 'series', group='series', default=None)
        if series is not None and series not in title:
            title = '%s, %s' % (series, title)
        info_dict = {
            'id': video_id,
            'title': title,
            'thumbnail': self._og_search_thumbnail(webpage),
            'description': self._og_search_description(webpage, default=''),
        }
        if mobj.group('type') == 'vod' and info_dict['description'] == '':
            info_dict.update({
                'description': self._html_search_regex(
                    r'(?s)<div\s+class=[\'"]opis.*?</div>',
                    self._download_webpage(url, video_id), 'description', group=0),
            })

        video_url = self._search_regex(
            r'0:{src:([\'"])(?P<url>.*?)\1', webpage, 'formats', group='url', default=None)
        if video_url is None:
            video_url = self._download_json(
                'http://www.tvp.pl/pub/stat/videofileinfo?video_id=%s' % video_id,
                video_id)['video_url']

        ext = video_url.rsplit('.', 1)[-1]
        if ext != 'ism/manifest':
            if '/' in ext:
                ext = 'mp4'
            info_dict.update({
                'ext': ext,
                'url': video_url,
            })
        else:
            m3u8_url = re.sub('([^/]*)\.ism/manifest', r'\1.ism/\1.m3u8', video_url)
            formats = self._extract_m3u8_formats(m3u8_url, video_id, 'mp4')
            info_dict.update({
                'formats': formats,
            })
        return info_dict
