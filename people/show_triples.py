#!/usr/bin/env/python

"""
    show_triples.py -- from the command line show the triples of any uri
    Version 0.1 MC 2014-07-22
     -- works as expected

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

import sys
from datetime import datetime
from vivofoundation import get_triples
from vivofoundation import VIVO_URI_PREFIX
import json

#   Start here

print sys.argv[1]
uri = VIVO_URI_PREFIX + sys.argv[1]
print uri
print json.dumps(get_triples(uri), indent=4)

print datetime.now(), "End"
