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

# use proxies to route requests over privoxy/tor
PROXYHOST = "localhost"
PROXYPORT = 8118

# default user-agent, check out random_agent.py for a dynamic alternative
DEFAULTUA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

# END OF CONFIG

__all__ = ["weedparams", "httpresolve", "unmeta", "unshorten", "main"]

import re, urllib2, cookielib, time, sys
from urlparse import urlparse, urlunparse
from itertools import ifilterfalse
import urllib, httplib
from lxml.html.soupparser import parse

utmRe=re.compile('(fb_(comment_id|ref|source|action_ids|action_types)|utm_(source|medium|campaign|content|term))=')
def weedparams(url):
    """
    removes annoying UTM params to urls.
    """
    pcs=urlparse(urllib.unquote_plus(url))
    tmp=list(pcs)
    tmp[4]='&'.join(ifilterfalse(utmRe.match, pcs.query.split('&')))
    return urlunparse(tmp)

def defaultua():
    """
    default user-agent generator function for httpresolve.
    """
    return DEFAULTUA

def httpresolve(url, ua=None, proxyhost=PROXYHOST, proxyport=PROXYPORT):
    """
    resolve one http resolve,
    specify a function which returns a ua string for some dynamism,
    and proxy parameters proxyhost and proxyport if necessary,
    return the new url and the httplib.response object.
    """
    if not ua: ua = defaultua
    # remove fb_ and utm_ tracking params
    url=weedparams(url)
    us=httplib.urlsplit(url)
    if not proxyhost:
        # connect directly
        if us.scheme=='http':
            conn = httplib.HTTPConnection(us.netloc)
            req = urllib.quote(url[7+len(us.netloc):])
        elif us.scheme=='https':
            conn = httplib.HTTPSConnection(us.netloc)
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
    url=weedparams(url)
    return (url, res)

def unmeta(url, res):
    """
    finds any meta redirects a httplib.response object that has
    text/html as content-type. url is the original url.
    """
    if res and (res.getheader('Content-type') or "").startswith('text/html'):
        root=parse(res)
        for x in root.xpath('//meta[@http-equiv="refresh"]'):
            newurl=x.get('content').split(';')
            if len(newurl)>1:
                newurl=newurl[1].strip()[4:]
                parts=httplib.urlsplit(urllib.unquote_plus(newurl))
                if parts.scheme and parts.netloc and parts.path:
                    url=newurl
    return url

def unshorten(url, cache=None, ua=None, **kwargs):
    """
    resolves all HTTP/META redirects and optionally caches them in any
    object supporting a __getitem__, __setitem__ interface, and a
    function returning user agent for the http request, if none is
    given the default is google bot.
    """
    prev=None
    origurl=url
    seen=[]
    while url!=prev:
        if url in seen: return ""
        seen.append(url)
        if cache:
            cached=cache[url]
            if cached: return cached
        prev=url
        url,root=httpresolve(url, ua=ua, **kwargs)
        if root:
            url=unmeta(url,root)
    if cache:
        cache[origurl]=url
    return url

def main():
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
            print unshorten(url,)
        else:
            print unshorten(sys.argv[1])

if __name__ == "__main__":
    main()
