"""
    test_tag_predicate.py -- given a full predicate such as
    http://www.w3.org/2002/07/owl#Thing return a tag URI predicate such as
    owl:Thing

    Version 0.1 MC 2014-07-25
    --  Initial version for tools 2.0
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from vivofoundation import tag_predicate
from datetime import datetime

print datetime.now(),"Start"
print tag_predicate("http://www.w3.org/2002/07/owl#Thing")
print tag_predicate("http://vivo.ufl.edu/ontology/vivo-ufl/Course")
print tag_predicate("http://www.w3.org/2004/02/skos/core#Concept")
print tag_predicate("http://vivoweb.org/ontology/core#FacultyMember")
print datetime.now(),"Finish"

