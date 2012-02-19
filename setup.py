import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "urlclean",
    version = "0.5.1",
    author = "Stefan Marsiske",
    author_email = "stefan.marsiske@gmail.com",
    description = ("Utilities to clean up URLs "),
    license = "AGPLv3+",
    keywords = "URL HTTP sanitizing privacy",
    packages = find_packages(),
    url = "http://packages.python.org/urlclean",
    py_modules=['urlclean' ],
    long_description=read('README.rst'),
    classifiers = ["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: GNU Affero General Public License v3",
                   "Environment :: Web Environment",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
                   "Topic :: Security",
                   "Topic :: Security :: Cryptography",
                   ],
)
