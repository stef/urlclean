
Welcome to urlclean's documentation!
************************************

urlclean provides functions:

* to follow a http redirect,

* to follow a HTML META redirect,

* to remove Urchin and Facebook tracker URL parameters

* that combines all these to unshorten and resolve various URLS

Try it out from the commandline::
   python -m urlclean <some url>

Contents:


Indices and tables
******************

* *Index*

* *Module Index*

* *Search Page*


Documentation for the Code
==========================

urlcleaner a module that resolves redirected urls and removes tracking
url params

urlclean.weedparams(url)

   removes Urchin Tracker and Facebook surveillance params from urls.

   Args:

      url (str):  The url to scrub of ugly params

   Returns:

      (str).  The return cleaned url

urlclean.httpresolve(url, ua=None, proxyhost='localhost', proxyport=8118)

   resolve one redirection of a http request.

   Args:

      url (str):  The url to follow one redirect

      ua (fn):  A function returning a User Agent string (optional)

      proxyhost (str):  http proxy server (optional)

      proxyport (int):  http proxy server port (optional)

   Returns: (str, httplib.response).  The return resolved url, and
      the response from the http query

urlclean.unmeta(url, res)

   Finds any meta redirects a httplib.response object that has
   text/html as content-type.

   Args:

      url (str):  The url to follow one redirect

      res (httplib.response):  a http.response object

   Returns: (str).  The return resolved url

urlclean.unshorten(url, cache=None, ua=None, >>**<<kwargs)

   resolves all HTTP/META redirects and optionally caches them in any
   object supporting a __getitem__, __setitem__ interface

   Args:

      url (str):  The url to follow one redirect

      cache (PersistentCryptoDict):  an optional PersistentCryptoDict
      instance

      ua (fn):  A function returning a User Agent string (optional),
      the default is googlebot.

      >>**<<kwargs (dict):  option proxy args for urlclean.httpresolve

   Returns: (str).  The return final cleaned url.
