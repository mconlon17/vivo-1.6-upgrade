"""
    test_update_position.py -- given a vivo position object and a source
    position object, generate add and sub rdf to update the vivo position
    to the values in the source

    Version 0.1 MC 2014-07-26
    --  Initial version.
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2013, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from vivopeople import update_position
from datetime import datetime

print datetime.now(),"Start"

vivo_position = { 'start_date': datetime(2013,1,1,0,0,0),
                  'uri': 'http://vivoposition_uri',
                  'dti_uri': 'http://dti_uri',
                  'position_label':'Warden of the Northern Marshes',
                  'person_uri': 'http://vivo.ufl.edu/individual/n3715',
                  'position_org_uri': 'http://vivo.ufl.edu/individual/xxx',
                  'position_rank': '1'
                  }
source_position = { 'start_date': datetime(2013,1,1,0,0,0),
                    'end_date': datetime(2014,3,23,0,0,0),
                  'position_label':'Warden of the Northern Marshes',
                  'person_uri': 'http://vivo.ufl.edu/individual/n3715',
                  'position_org_uri': 'http://vivo.ufl.edu/individual/xxx',
                  'position_rank': '2'
                  }
[add, sub] = update_position(vivo_position, source_position)
print "\nCase 1. Update end date and rank.\nVIVO\n",\
    vivo_position,"\nSource\n",source_position,"\nAdd\n",add,"\nSub\n",sub

vivo_position = { 'start_date': datetime(2013,1,1,0,0,0),
                  'uri': 'http://vivoposition_uri',
                  'dti_uri': 'http://dti_uri',
                  'position_label':'Warden of the Northern Marshes',
                  'person_uri': 'http://vivo.ufl.edu/individual/n3715',
                  'position_org_uri': 'http://vivo.ufl.edu/individual/xxx',
                  'position_rank': '1'
                  }
source_position = {'start_date': datetime(2013,1,1,0,0,0),
                  'position_label':'Warden of the Northern Marshes',
                  'person_uri': 'http://vivo.ufl.edu/individual/n3715',
                  'position_org_uri': 'http://vivo.ufl.edu/individual/xxx',
                  'position_rank': '1'
                  }
[add, sub] = update_position(vivo_position, source_position)
print "\nCase 2. Nothing to do.\nVIVO\n",\
    vivo_position,"\nSource\n",source_position,"\nAdd\n",add,"\nSub\n",sub


vivo_position = { 'uri': 'http://whatever'}
source_position = { 'start_date': datetime(2013,1,1,0,0,0),
                    'end_date': datetime(2014,3,23,0,0,0),
                  'position_label':'Warden of the Northern Marshes',
                  'person_uri': 'http://vivo.ufl.edu/individual/n3715',
                  'position_org_uri': 'http://vivo.ufl.edu/individual/xxx',
                  'position_rank': '2'
                  }
[add, sub] = update_position(vivo_position, source_position)
print "\nCase 3. Adding a position.\nVIVO\n",\
    vivo_position,"\nSource\n",source_position,"\nAdd\n",add,"\nSub\n",sub

print datetime.now(),"Finish"

