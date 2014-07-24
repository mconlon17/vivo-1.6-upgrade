"""
    test_get_vcard.py -- Given the URI of a vcard, return values and uris
    assocuiated withe vcard.  Handle repeating values such as telephone
    and email.

    Version 0.1 MC 2014-07-24
    --  Initial version for tools 2.0
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from vivopeople import get_vcard
from datetime import datetime
import json

print datetime.now(),"Start"
print "\n",json.dumps(get_vcard("http://vivo.ufl.edu/individual/n6754"),
                      indent=4)
print datetime.now(),"Finish"
