"""
    test_get_vivo_uri.py -- return a valid, unused, vivo URI

    Version 0.1 MC 2013-12-28
    --  Initial version.
    Version 0.2 MC 2014-07-21
    --  Formatting improvements. Tested with 1.6

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"

from vivofoundation import get_vivo_uri 
from datetime import datetime

print datetime.now(),"Start"

for i in range(0,9):
    print get_vivo_uri()

print datetime.now(),"Finished"
