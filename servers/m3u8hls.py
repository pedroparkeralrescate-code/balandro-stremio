# -*- coding: utf-8 -*-


import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Para archivos .m3u8 que Kodi no reproduce con el siguiente aviso:
# NOTICE: Creating video codec with codec id: 61
# NOTICE: CDVDVideoCodecFFmpeg::Open() Using codec: PNG (Portable Network Graphics) image

from platformcode import logger, platformtools

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    from lib.m3u8server import Client
    c = Client(url=page_url, is_playing_fnc=platformtools.is_playing)
    f = c.get_file()
    if f: video_urls.append(['m3u8', f])
    
    return video_urls
