"""
    test_get_person.py -- Given a URIof a person entity in VIVO, return a
    python sturcture containing attrbutes of the person

    Version 0.1 MC 2013-12-27
    --  Initial version.
    Version 0.2 MC 2014-07-24
    --  Updated for tools 2.0
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"

from vivopeople import get_person
from datetime import datetime
import json

print datetime.now(),"Start"
print "\n",json.dumps(get_person("http://vivo.ufl.edu/individual/n3715",
                                 get_contact=False), indent=4)
print "\n",json.dumps(get_person("http://vivo.ufl.edu/individual/n3715"),
                      indent=4)
print "\n",json.dumps(get_person("http://vivo.ufl.edu/individual/n4452"),
                      indent=4)
print "\n",json.dumps(get_person("http://vivo.ufl.edu/individual/n3428"),
                      indent=4)
print datetime.now(),"Finish"
