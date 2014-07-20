#!/usr/bin/env/python

"""
    person-ingest.py: Given person data from HR, compare to VIVO and
    create addition and subtration RDF for VIVO to create and update
    people, positions, contact information and current status in
    accordance with UF privacy practices.

    There are three cases:

    Case 1: The person is in HR, but not in VIVO.  If the person meets the
    inclusion criteria, they will be added to VIVO, marked as Current and a
    position will be added.

    Case 2: The person is in VIVO, but not in HR.  The Current assertion will be
    removed along with contact information and the person will remain in VIVO.

    Case 3: The person is in VIVO and in HR.  The person will be marked as
    Current, the current HR position will be updated or added as needed.

    To Do:
    Just about everything
    Handle case 2 (separate program!?)

    Future enhancements:
     -- For case 2, close end dates for positions with explicit HR data rather
        than inferring an end date via the absence of HR data
     -- read external sources into standard tag name structures.  Do not carry
        local names (JOBCODE_DESCRIPTION) into the code.
     -- explore data source and process for assigning person type Librarian. UF
        marks librarians as Faculty in HR data.  No indication that the person
        is a librarian by salary plan
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "2.00"

from datetime import datetime
from vivofoundation import rdf_header
from vivofoundation import rdf_footer
from vivofoundation import find_vivo_uri
from vivofoundation import get_vivo_uri
from vivofoundation import read_csv
from vivopeople import get_person
from operator import itemgetter
import codecs
import sys
import os
import vivofoundation as vf

# Prepare, add, update

def prepare_people(position_file_name):
    """
    Given a UF position file, return a list of people to be added to VIVO.
    Process each data value.  Reject bad values.  Reject things that must
    be found in VIVO.  Return clean data ready to add. If more than one
    position qualifies for inclusion, use the last one in the file.
    """
    people = {}
    positions = read_csv(position_file_name)
    for row, position in sorted(positions.items(), key=itemgetter(1)):
        ufid = position['UFID']
        position['uri'] = find_vivo_uri('ufVivo:ufid', ufid)
        people[ufid] = position
    return people

def add_person(person):
    """
    Add a person to VIVO
    """
    add = ""
    person_uri = vivo_get_uri()
    return [add, person_uri]

def update_person(vivo_person, source_person):
    """
    Given a data structure representing a person in VIVO, and a data
    structure rpesenting the same person with data values from source
    systems, generate the ADD and SUB RDF necessary to update the VIVO
    person's data values to the corresponding values in the source
    """
    ardf = ""
    srdf = ""
    return [ardf, srdf]

# Start here

if len(sys.argv) > 1:
    input_file_name = str(sys.argv[1])
else:
    input_file_name = "position_test.txt"
file_name, file_extension = os.path.splitext(input_file_name)

add_file = codecs.open(file_name+"_add.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
sub_file = codecs.open(file_name+"_sub.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
log_file = sys.stdout
##log_file = codecs.open(file_name+"_log.txt", mode='w', encoding='ascii',
##                       errors='xmlcharrefreplace')
exc_file = codecs.open(file_name+"_exc.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')

ardf = rdf_header()
srdf = rdf_header()

print >>log_file, datetime.now(), "Start"
print >>log_file, datetime.now(), "Person Ingest Version", __version__
print >>log_file, datetime.now(), "VIVO Foundation Version", vf.__version__
print >>log_file, datetime.now(), "Read Position Data"
people = prepare_people(input_file_name)
print >>log_file, datetime.now(), "Position data has", len(people),\
    "people"

# Main loop

for source_person in people.values():

    print
    print "Consider"
    print
    print source_person
    
    if 'uri' in source_person and source_person['uri'] is not None:
        print >>log_file, "Updating person at", source_person['uri']
        vivo_person = get_person(source_person['uri'])
        [add, sub] = update_person(vivo_person, source_person)
        ardf = ardf + add
        srdf = srdf + sub
    else:
        print >>log_file, "Adding person at", source_person['uri']
        [add, person_uri] = add_person(source_person)
        vivo_person = {'uri': source_person['uri']}
        ardf = ardf + add
        [add, sub] = update_person(vivo_person, source_person)
        ardf = ardf + add
        srdf = srdf + sub

adrf = ardf + rdf_footer()
srdf = srdf + rdf_footer()
add_file.write(adrf)
sub_file.write(srdf)
add_file.close()
sub_file.close()
print >>log_file, datetime.now(), "Finished"
