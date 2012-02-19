#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Downloader for http://indavideo.hu/
Author: András Veres-Szentkirályi <vsza@vsza.hu>, Stefan Marsiske <stefan.marsiske@gmail.com>
License: MIT
"""

from lxml import html
from urllib2 import urlopen
from urllib import unquote_plus
from urlparse import urlsplit
import re

__prefs__ = ('720', '360', 'webm')
__amftpl__ = ('\0\x03\0\0\0\x01\0!player.playerHandler.getVideoData\0\x02/1'
        '\0\0\0!\n\0\0\0\x04\x02\0\n{vid}\0@(\0\0\0\0\0\0\x02\0\0\x02\0\0')

def convert(url):
    """Downloads the video from the URL in the url parameter"""
    if not urlsplit(unquote_plus(url))[1].endswith('indavideo.hu'):
        return url
    videos = getvideos(url)
    if not videos: return url
    return preferred(videos)

def preferred(videos):
    """Returns the preferred URL from the iterable in the videos parameter"""
    for pref in __prefs__:
        for video in videos:
            if pref in video:
                return video
    return videos[0]

def url2vid(url):
    """Returns the ID of the video on the URL in the url parameter"""
    video = html.parse(urlopen(url)).getroot()
    if video == None: return
    video_src = video.xpath('/html/head/link[@rel = "video_src"]/@href'
        ' | /html/head/meta[@property="og:video"]/@content')[0]
    return re.search('vID=([^&]+)&', video_src).group(1)

def getvideos(url):
    """Returns URLs that contain the video on the URL in the url parameter"""
    vid=url2vid(url)
    if vid == None: return
    amfreq = __amftpl__.format(vid=vid)
    amfresp = urlopen('http://amfphp.indavideo.hu/gateway.php', amfreq).read()
    return set(re.findall(r'http://[a-zA-Z0-9/._]+\.(?:mp4|webm)', amfresp))
