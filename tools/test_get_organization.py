"""
    test_get_organization.py -- Given a URI of an organization entity in VIVO,
    return a python sturcture containing attributes of the organization

    Version 0.1 MC 2013-12-27
    --  Initial version.
    Version 0.2 MC 2014-07-25
    --  Updated for tools 2.0
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"

from vivofoundation import get_organization
from datetime import datetime

print datetime.now(),"Start"
print "\n",get_organization("http://vivo.ufl.edu/individual/n2003")
print "\n",get_organization("http://vivo.ufl.edu/individual/n8763427")
print datetime.now(),"Finish"
