import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "urlclean",
    version = "0.4.1",
    author = "Stefan Marsiske",
    author_email = "stefan.marsiske@gmail.com",
    description = ("Utilities to clean up URLs "),
    license = "AGPLv3+",
    keywords = "URL HTTP sanitizing privacy",
    url = "http://packages.python.org/urlclean",
    py_modules=['urlclean' ],
    long_description=read('README.rst'),
    #classifiers=["Classifier: Development Status :: 4 - Beta",
    #             "License :: OSI Approved :: GNU Affero General Public License v3",
    #             ],
)
