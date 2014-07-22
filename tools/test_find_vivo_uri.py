"""
    test_find_vivo_uri.py -- return the first VIVO URI that staisfies a
    match on predicate and value

    Version 0.1 MC 2014-03-25
    --  Initial version.
    Version 0.2 MC 2014-07-22
    --  Updated for tools 2.0

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"

from vivofoundation import find_vivo_uri
from datetime import datetime

print datetime.now(),"Start"

print find_vivo_uri("ufv:deptID","29680100") # Org from deptID
print find_vivo_uri("rdfs:label","Clinical and Translational Science Institute") # Org from deptID
print find_vivo_uri("vivo:eRACommonsId","mconlon") # Person from eRACommons
print find_vivo_uri("vivo:orcidId","0000-0002-1304-8447") # person from ORCID
print find_vivo_uri("ufVivo:ISNI","0000 0001 2193 2008") # No such predicate
print find_vivo_uri("ufVivo:isni","0000 0001 2193 2008") # Org from ISNI
print find_vivo_uri("bibo:issn","0028-4793") # Journal from ISSN
print find_vivo_uri("bibo:issn","9876-5432") # No such ISSN
print find_vivo_uri("bibo:pmid","12763083") # paper from PubMed ID

print datetime.now(),"Finished"
