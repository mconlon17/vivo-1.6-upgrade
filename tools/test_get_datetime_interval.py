"""
    test_get_datetime_interval.py -- Given a URI of a datetime interval, return
    a python structure with the attributes of the date time interval

    Version 0.1 MC 2013-12-27
    --  Initial version
    Version 0.2 MC 2014-07-25
    --  Updated for tools 2.0
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2013, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"

from vivofoundation import get_datetime_interval
from datetime import datetime

print datetime.now(), "Start"
datetime_intervals = [
    "http://vivo.ufl.edu/individual/n5854",
    "http://vivo.ufl.edu/individual/n5807",
    "http://vivo.ufl.edu/individual/n6327"
    ]
for datetime_interval in datetime_intervals:
    print "\n", get_datetime_interval(datetime_interval)
print datetime.now(), "Finish"
