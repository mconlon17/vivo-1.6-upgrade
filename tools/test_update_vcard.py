"""
    test_update_vcard.py -- given a vivo vcard object and a source
    vcard object, generate add and sub rdf to update the vivo vcard
    to the values in the source

    Version 0.1 MC 2014-07-26
    --  Initial version.
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from vivopeople import update_vcard
from vivopeople import get_vcard
from datetime import datetime
import json

print datetime.now(),"Start"

vivo_vcard = get_vcard('http://vivo.ufl.edu/individual/n6754')
source_vcard = { 'name':{'additional_name': None,
                         'honorific_suffix':'Esq',
                         },
                 'title':'Chief Cook and Bottle Washer',
                 }
[add, sub] = update_vcard(vivo_vcard, source_vcard)
print "\nCase 1. Remove middle name.  Change name suffix and title.\nVIVO\n",\
    json.dumps(vivo_vcard, indent=4), "\nSource\n", \
    json.dumps(source_vcard, indent=4), "\nAdd\n", add, "\nSub\n", sub

print datetime.now(),"Finish"

