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
    Test cases for all inclusion/exclusion
    Add UF Ontology to vagrant
    Begin output processes
    Handle case 2 (separate program)

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
from vivopeople import get_position_type
from vivopeople import improve_jobcode_description
from vivopeople import repair_phone_number
from vivopeople import repair_email
from operator import itemgetter
import codecs
import sys
import os
import vivofoundation as vf

def comma_space(s):
    """
    insert a space after every comma in s unless s ends in a comma
    """
    k = s.find(',')
    if k > -1 and k < len(s)-1 and s[k+1] != " ":
        s = s[0:k] + ', ' + comma_space(s[k+1:])
    return s

def ok_deptid(deptid, deptid_exceptions):
    """
    Some deptids are in an exception dictionary of patterns.  If a person is
    in one of these departments, they will not be listed in VIVO.

    Deptids in the exception dictionary are regular expressions

    Given a dept id, the deptid exception list is checked.  True is
    returned if the deptid is not matched.  False is returned
    if the deptid is matched.
    """
    import re
    ok = True
    for pattern_string in deptid_exceptions.keys():
        pattern = re.compile(pattern_string)
        if pattern.search(deptid) is not None:
            ok = False
            break
    return ok

# Prepare, add, update

def prepare_people(position_file_name):
    """
    Given a UF position file, return a list of people to be added to VIVO.
    Process each data value.  Reject bad values.  Return clean data ready
    to add. If more than one position qualifies for inclusion, use the last
    one in the file.

    Requires
    -- a shelve of privacy data keyed by UFID containing privacy flags
    -- a shelve of contact data keyed by UFID
    -- a shelve of deptid exception patterns
    -- a shelve of UFIDs that will not be touched in VIVO
    -- a shelve of URI that will not be touched in VIVO
    """
    import shelve
    privacy = shelve.open('privacy')
    contact = shelve.open('contact')
    deptid_exceptions = shelve.open('deptid_exceptions')
    ufid_exceptions = shelve.open('ufid_exceptions')
    uri_exceptions = shelve.open('uri_exceptions')
    position_exceptions = shelve.open('position_exceptions')
    people = {}
    positions = read_csv(position_file_name)
    for row, position in sorted(positions.items(), key=itemgetter(1)):
        person = {}
        ufid = str(position['UFID'])
        if ufid in ufid_exceptions:
            exc_file.write(ufid+' in ufid_exceptions.  Will be skipped.\n')
            continue
        person['ufid'] = ufid
        person['uri'] = find_vivo_uri('ufv:ufid', ufid)
        if person['uri'] is not None and str(person['uri']) in uri_exceptions:
            exc_file.write(person['uri']+' in uri_exceptions.'+\
            '  Will be skipped.\n')
            continue
        if ok_deptid(position['DEPTID'], deptid_exceptions):
            person['position_deptid'] = position['DEPTID']
        else:
            exc_file.write(ufid+' has position in department '+\
                position['DEPTID']+' which is on the department exception '+
                ' list.  No position will be added.\n')
            person['position_deptid'] = None
        person['type'] = get_position_type(position['SAL_ADMIN_PLAN'])
        if person['type'] is None:
            exc_file.write(ufid+' invalid salary plan '+\
                           position['SAL_ADMIN_PLAN']+'\n')
            continue
        if ufid not in privacy:
            exc_file.write(ufid+' not found in privacy data\n')
            continue
        flags = privacy[ufid]
        if flags['UF_PROTECT_FLG'] == 'Y':
            exc_file.write(ufid+' has protect flag Y\n')
            continue
        if flags['UF_SECURITY_FLG'] == 'Y':
            exc_file.write(ufid+' has security flag Y\n')
            continue
        if ufid not in contact:
            exc_file.write(ufid+' not found in contact data\n')
            continue
        info = contact[ufid]
        person['first_name'] = info['FIRST_NAME'].title()
        person['last_name'] = info['LAST_NAME'].title()
        person['middle_name'] = info['MIDDLE_NAME'].title()
        person['name_suffix'] = info['NAME_SUFFIX'].title()
        person['name_prefix'] = info['NAME_PREFIX'].title()
        person['display_name'] = comma_space(info['DISPLAY_NAME'].title())
        person['gatorlink'] = info['GATORLINK'].lower()
        if info['WORKINGTITLE'].upper() == info['WORKINGTITLE']:
            person['preferred_title'] = \
                improve_jobcode_description(position['JOBCODE_DESCRIPTION'])
        else:
            person['preferred_title'] = info['WORKINGTITLE']
        person['primary_email'] = repair_email(info['UF_BUSINESS_EMAIL'])
        person['phone'] = repair_phone_number(info['UF_BUSINESS_PHONE'])
        person['fax'] = repair_phone_number(info['UF_BUSINESS_FAX'])
        if ok_deptid(info['HOME_DEPT'], deptid_exceptions):
            person['home_deptid'] = info['HOME_DEPT']
        else:
            exc_file.write(ufid+' has home department on exception list.'+\
                ' This person will not be added to VIVO.\n')
            continue
        person['start_date'] = position['START_DATE']
        person['end_date'] = position['END_DATE']
        person['description'] = \
            improve_jobcode_description(position['JOBCODE_DESCRIPTION'])
        if str(person['description']) in position_exceptions:
            exc_file.write(description +' found in position exceptions.' +\
                'The position will not be added.\n')
            person['description'] = None
        person['hr_position'] = position['HR_POSITION'] == "1"
        people[ufid] = person
    privacy.close()
    contact.close()
    deptid_exceptions.close()
    ufid_exceptions.close()
    uri_exceptions.close()
    position_exceptions.close()
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
##        vivo_person = get_person(source_person['uri'])
##        [add, sub] = update_person(vivo_person, source_person)
##        ardf = ardf + add
##        srdf = srdf + sub
    else:
        print >>log_file, "Adding person at", source_person['uri']
        [add, person_uri] = add_person(source_person)
        vivo_person = {'uri': person_uri}
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
exc_file.close()
print >>log_file, datetime.now(), "Finished"
