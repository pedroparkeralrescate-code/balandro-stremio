# -*- coding: utf-8 -*-


import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    data = scrapertools.httptools.downloadpage(page_url).data

    matches = scrapertools.find_multiple_matches(data, '<source src="([^"]+)"')
    for url in matches:
        video_urls.append(['mp4', url])

    return video_urls
