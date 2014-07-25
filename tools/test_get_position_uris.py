"""
    test_get_position_uris.py -- Given a person URI, get the uris of the person's
    positions.  Returns an empty list if none.

    Version 0.1 MC 2014-07-25
    --  Initial version
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from vivopeople import get_position_uris
from datetime import datetime

#  Test cases for get_position_uris

print datetime.now(), "Start"

print "\nConlon"
print get_position_uris("http://vivo.ufl.edu/individual/n3715")

print "\nAberta"
print get_position_uris("http://vivo.ufl.edu/individual/n3428")

print datetime.now(), "Finish"

