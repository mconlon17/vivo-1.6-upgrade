"""
    test_get_types.py -- Given a URI, get the types

    Version 0.1 MC 2014-06-21
    --  Initial version.
    Version 0.2 MC 2014-07-25
    --  Updated for Tools 2.0
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"

from vivofoundation import get_types
from datetime import datetime

#  Test cases for access and display functions

print datetime.now(), "Start"

print "\nPosition"
print get_types("http://vivo.ufl.edu/individual/n7320")

print "\nDateTime"
print get_types("http://vivo.ufl.edu/individual/n4872")


print "\nDateTimeInterval"
print get_types("http://vivo.ufl.edu/individual/n5807")

print "\nOrganization"
print get_types("http://vivo.ufl.edu/individual/n2003")


print "\nAuthorship"
print get_types("http://vivo.ufl.edu/individual/n148010391")

print "\nRole"
print get_types("http://vivo.ufl.edu/individual/n2926")

print "\nPerson"
print get_types("http://vivo.ufl.edu/individual/n3715")

print "\nNot Found"
print get_types("http://vivo.ufl.edu/notfound")

print "\nPublication Venue"
print get_types("http://vivo.ufl.edu/individual/n378789540")

print "\nPaper"
print get_types("http://vivo.ufl.edu/individual/n4703866415")

print "\nGrant"
print get_types("http://vivo.ufl.edu/individual/n5432")

print datetime.now(), "Finish"

