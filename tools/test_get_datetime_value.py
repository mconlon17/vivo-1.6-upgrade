"""
    test_get_datetime_value.py -- Given a URI of a datetime value, return
    a python structure withthe attributes of the date time

    Version 0.1 MC 2013-12-27
    --  Initial version.
    Version 0.2 MC 2014-07-26
    --  Updated for tools 2.0

"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2013, University of Florida"
__license__     = "BSD 3-Clause license"
__version__     = "0.2"

from vivofoundation import get_datetime_value
from datetime import datetime

print datetime.now(),"Start"
datetime_value_uris = [
    "http://vivo.ufl.edu/individual/n3413",
    "http://vivo.ufl.edu/individual/n838"
    ]
for datetime_value_uri in datetime_value_uris:
    print "\n", get_datetime_value(datetime_value_uri)
print datetime.now(),"Finish"
