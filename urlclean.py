#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of urlcleaner
#
#  urlcleaner is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  urlcleaner is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with urlcleaner.  If not, see <http://www.gnu.org/licenses/>.
#
# (C) 2012- by Stefan Marsiske, <stefan.marsiske@gmail.com>

"""urlcleaner a module that resolves redirected urls and removes tracking url params

.. moduleauthor:: Stefan Marsiske, <stefan.marsiske@gmail.com>

"""

# use proxies to route requests over privoxy/tor
#PROXYHOST = "localhost"
#PROXYPORT = 8118
PROXYHOST = ""
PROXYPORT = ""

# default user-agent, check out random_agent.py for a dynamic alternative
DEFAULTUA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

# END OF CONFIG

__all__ = ["weedparams", "httpresolve", "unmeta", "unshorten", "main"]

import re, urllib2, cookielib, time, sys
from urlparse import urlsplit, urlunsplit
from itertools import ifilterfalse
from cStringIO import  StringIO
import urllib, httplib
from lxml.html.soupparser import parse
import plugins

utmRe=re.compile('(fb_(comment_id|ref|source|action_ids|action_types)|utm_(source|medium|campaign|content|term))=')
ytRe=re.compile('(v|p)=')
def weedparams(url):
    """
    removes Urchin Tracker and Facebook surveillance params from urls.

    Args:

       url (str):  The url to scrub of ugly params

    Returns:

       (str).  The return cleaned url
    """
    pcs=urlsplit(urllib.unquote_plus(url))
    tmp=list(pcs)
    tmp[2]= urllib.quote_plus(tmp[2],'~áÁéÉíÍóÓöÖőŐúÚüÜűŰłŁß/')
    if tmp[1].endswith('youtube.com'):
        tmp[3]= ([x for x in pcs.query.split('&') if ytRe.match(x)] or [None])[0]
    elif tmp[1].endswith('vimeo.com'):
        tmp[3]= ([x for x in pcs.query.split('&') if x.startswith('clip_id=')] or [None])[0]
    else:
        tmp[3]= urllib.quote_plus('&'.join(ifilterfalse(utmRe.match,
                                                        pcs.query.split('&'))),
                                  'áÁéÉíÍóÓöÖőŐúÚüÜűŰłŁß=&/')
    return urlunsplit(tmp)

def _defaultua():
    """
    Default user-agent generator function for httpresolve.
    """
    return DEFAULTUA

def httpresolve(url, ua=None, proxyhost=PROXYHOST, proxyport=PROXYPORT):
    """
    resolve one redirection of a http request.

    Args:

       url (str):  The url to follow one redirect

       ua (fn):  A function returning a User Agent string (optional)

       proxyhost (str):  http proxy server (optional)

       proxyport (int):  http proxy server port (optional)

    Returns: (str, httplib.response).  The return resolved url, and
       the response from the http query

    """
    if not ua: ua = _defaultua
    # remove fb_ and utm_ tracking params
    us=httplib.urlsplit(url)
    if not proxyhost:
        # connect directly
        if us.scheme=='http':
            conn = httplib.HTTPConnection(us.netloc, timeout=5)
            req = urllib.quote(url[7+len(us.netloc):])
        elif us.scheme=='https':
            conn = httplib.HTTPSConnection(us.netloc, timeout=5)
            req = urllib.quote(url[8+len(us.netloc):])
    else:
        # connect using proxy
        conn = httplib.HTTPConnection(proxyhost,proxyport)
        req = url
    #conn.set_debuglevel(9)
    headers={'User-Agent': ua(),
             'Accept': '*/*',}
    conn.request("GET", url, None, headers)
    res = conn.getresponse()
    if res.status in [301, 304]:
        url = res.getheader('Location')
    return (weedparams(url), res)

def unmeta(url, res):
    """
    Finds any meta redirects a httplib.response object that has
    text/html as content-type.

    Args:

       url (str):  The url to follow one redirect

       res (httplib.response):  a http.response object

    Returns: (str).  The return resolved url

    """
    if res and (res.getheader('Content-type') or "").startswith('text/html'):
        size=65535
        if res.getheader('Content-Length'):
           try:
              tmp=int(res.getheader('Content-length'))
              if tmp<65535:
                 size=tmp
           except:
              print "wrong content-length:",res.getheader('Content-length')

        root=parse(StringIO(res.read(size)))
        for x in root.xpath('//meta[@http-equiv="refresh"]'):
            newurl=x.get('content').split(';')
            if len(newurl)>1:
                newurl=newurl[1].strip()[4:]
                parts=httplib.urlsplit(urllib.unquote_plus(newurl))
                if parts.scheme and parts.netloc:
                    url=newurl
    return weedparams(url)

def unshorten(url, cache=None, ua=None, **kwargs):
    """
    resolves all HTTP/META redirects and optionally caches them in any
    object supporting a __getitem__, __setitem__ interface

    Args:

       url (str):  The url to follow one redirect

       cache (PersistentCryptoDict):  an optional PersistentCryptoDict instance

       ua (fn):  A function returning a User Agent string (optional), the default is googlebot.

       **kwargs (dict):  optional proxy args for urlclean.httpresolve (default: localhost:8118)

    Returns: (str).  The return final cleaned url.

    """
    prev=None
    origurl=url
    seen=[]
    while url!=prev:
        # abort recursions
        if url in seen: return ""
        seen.append(url)
        if cache:
            cached=cache[url]
            if cached: return cached
        url=weedparams(url)
        prev=url
        url,root=httpresolve(url, ua=ua, **kwargs)
        url=unmeta(url,root)
    for p in plugins.modules:
        url=p.convert(url)
        try:
            url=p.convert(url)
        except:
            pass # ignore plugin failures
    if cache:
        cache[origurl]=url
    return url

def _main():
    if len(sys.argv)>1:
        if sys.argv[1]=='test':
            url="http://bit.ly/xJ5pK2"
            # uncached
            print unshorten(url)
            # start caching
            from pcd import PersistentCryptoDict
            cache=PersistentCryptoDict()
            print unshorten(url, cache=cache)
            # much faster resolve now
            print unshorten(url, cache=cache)
            # slower again
            print unshorten(url)
        else:
            print unshorten(sys.argv[1])

if __name__ == "__main__":
    _main()
