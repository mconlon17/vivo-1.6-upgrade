"""
    test_get_position.py -- Given a URI of a position, return a python
    structure representing the attributes of the position

    Version 0.1 MC 2013-12-27
    --  Initial version
    Version 0.2 MC 2014-07-25
    --  Updated for Tools 2.0

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2013, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"

from vivopeople import get_position
from datetime import datetime
import json

print datetime.now(), "Start"
position_uris = [
    "http://vivo.ufl.edu/individual/n7320",
    "http://vivo.ufl.edu/individual/n6535"
    ]
for position_uri in position_uris:
    print "\n", json.dumps(get_position(position_uri), indent=4)
print datetime.now(), "Finish"
