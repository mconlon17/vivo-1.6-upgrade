"""
    test_get_triples.py -- Given a URI, get the triples for the URI

    Version 0.1 MC 2013-12-27
    --  Initial version.
    Version 0.2 MC 2014-07-15
    --  Add Study
    Version 0.3 MC 2014-07-22
    --  Upgraded for tools 2.0
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.3"

from vivofoundation import get_triples

#  Test cases for get_triples

print "\nDateTime"
print get_triples("http://vivo.ufl.edu/individual/n7860108656")

print "\nDateTimeInterval"
print get_triples("http://vivo.ufl.edu/individual/n182882417")

print "\nOrganization"
print get_triples("http://vivo.ufl.edu/individual/n8763427")

print "\nAuthorship"
print get_triples("http://vivo.ufl.edu/individual/n148010391")

print "\nRole"
print get_triples("http://vivo.ufl.edu/individual/n1864549239")

print "\nPerson"
print get_triples("http://vivo.ufl.edu/individual/n3715")

print "\nNot Found"
print get_triples("http://vivo.ufl.edu/notfound")

print "\nPublication Venue"
print get_triples("http://vivo.ufl.edu/individual/n378789540")

print "\nPaper"
print get_triples("http://vivo.ufl.edu/individual/n4703866415")

print "\nGrant"
print get_triples("http://vivo.ufl.edu/individual/n614029206")

print "\nStudy"
print get_triples("http://vivo.ufl.edu/individual/n42801")

