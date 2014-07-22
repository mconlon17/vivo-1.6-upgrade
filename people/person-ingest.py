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
from vivofoundation import untag_predicate
from vivofoundation import assert_resource_property
from vivofoundation import assert_data_property
from vivopeople import get_person
from vivopeople import get_position_type
from vivopeople import improve_jobcode_description
from vivopeople import repair_phone_number
from vivopeople import repair_email
from operator import itemgetter
import codecs
import sys
import os
import json
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

    Field by field.  Check.  Improve.  Dereference. Generate exceptions.
    The result should be clean, complete data, ready to be added.

    Requires
    -- a shelve of privacy data keyed by UFID containing privacy flags
    -- a shelve of contact data keyed by UFID
    -- a shelve of deptid exception patterns
    -- a shelve of UFIDs that will not be touched in VIVO
    -- a shelve of URI that will not be touched in VIVO
    """
    import shelve
    person_type_table = {
        'faculty':'vivo:FacultyMember',
        'postdoc':'vivo:Postdoc',
        'courtesy-faculty':'vivo:CourtesyFaculty',
        'clinical-faculty':'ufv:ClinicalFaculty',
        'housestaff':'ufv:Housestaff',
        'temp-faculty':'ufv:TemporaryFaculty',
        'non-academic':'vivo:NonAcademic'
        }
    privacy = shelve.open('privacy')
    contact = shelve.open('contact')
    deptid_exceptions = shelve.open('deptid_exceptions')
    ufid_exceptions = shelve.open('ufid_exceptions')
    uri_exceptions = shelve.open('uri_exceptions')
    position_exceptions = shelve.open('position_exceptions')
    people = {}
    positions = read_csv(position_file_name)
    for row, position in sorted(positions.items(), key=itemgetter(1)):
        anyerrors = False
        person = {}
        ufid = str(position['UFID'])
        if ufid in ufid_exceptions:
            exc_file.write(ufid+' in ufid_exceptions.  Will be skipped.\n')
            anyerrors = True
        person['ufid'] = ufid
        person['uri'] = find_vivo_uri('ufv:ufid', ufid)
        if person['uri'] is not None and str(person['uri']) in uri_exceptions:
            exc_file.write(person['uri']+' in uri_exceptions.'+\
            '  Will be skipped.\n')
            anyerrors = True
        person['hr_position'] = position['HR_POSITION'] == "1"
        if ok_deptid(position['DEPTID'], deptid_exceptions):
            person['position_deptid'] = position['DEPTID']
            depturi = find_vivo_uri('ufv:deptID', position['DEPTID'])
            person['position_depturi'] = depturi
            if depturi is None:
                exc_file.write(ufid+' has deptid ' + position['DEPTID'] +\
                               ' not found.\n')
                anyerrors = True
        else:
            exc_file.write(ufid+' has position in department '+\
                position['DEPTID']+' which is on the department exception '+
                ' list.  No position will be added.\n')
            person['position_deptid'] = None
        if person['hr_position'] == True:
            person['position_type'] = \
                get_position_type(position['SAL_ADMIN_PLAN'])
            if person['position_type'] is None:
                exc_file.write(ufid+' invalid salary plan '+\
                               position['SAL_ADMIN_PLAN']+'\n')
                anyerrors = True
        else:
            person['position_type'] = None
        if person['position_type'] in person_type_table:
            person['person_type'] = \
                untag_predicate(person_type_table[\
                    person['position_type']])
        elif person['position_type'] is not None:
            exc_file.write(ufid+' has position type ' +
                person['position_type']+' not in person_type_table\n')
            anyerrors = True
        if ufid not in privacy:
            exc_file.write(ufid+' not found in privacy data\n')
            anyerrors = True
        else:
            person['uf_privacy'] = privacy[ufid]['UF_PROTECT_FLG']
            if person['uf_privacy'] == 'Y':
                exc_file.write(ufid+' has protect flag Y\n')
                anyerrors = True
        if ufid not in contact:
            exc_file.write(ufid+' not found in contact data\n')
            anyerrors = True
        else:
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
                homedept_uri = find_vivo_uri('ufv:deptID', info['HOME_DEPT'])
                person['homedept_uri'] = homedept_uri
                if homedept_uri is None:
                    exc_file.write(ufid + ' has home department deptid '+\
                        info['HOME_DEPT'] + ' not found in VIVO\n')
            else:
                exc_file.write(ufid+' has home department on exception list.'+\
                    ' This person will not be added to VIVO.\n')
                anyerrors = True
        person['start_date'] = position['START_DATE']
        person['end_date'] = position['END_DATE']
        person['description'] = \
            improve_jobcode_description(position['JOBCODE_DESCRIPTION'])
        if str(person['description']) in position_exceptions:
            exc_file.write(ufid+' has position description '+
                person['description'] +\
                ' found in position exceptions.' +\
                'The position will not be added.\n')
            person['description'] = None
        if not anyerrors:
            people[row] = person
    privacy.close()
    contact.close()
    deptid_exceptions.close()
    ufid_exceptions.close()
    uri_exceptions.close()
    position_exceptions.close()
    return people

def add_vcard(a,b):
    return ""

def add_position(a,b):
    return ""

def add_person(person):
    """
    Add a person to VIVO.  The person structure may have any number of
    elements.  These elements may represent direct assertions (label,
    ufid, homeDept), vcard assertions (contact info, name parts),
    and/or position assertions (title, tye, dept, start, end dates)
    """
    ardf = ""
    person_uri = get_vivo_uri()

    # Add direct assertions

    person_type = person['person_type']
    ardf = ardf + assert_resource_property(person_uri, 'rdfs:type', person_type)

    direct_data_preds = {'ufid':'ufv:ufid',
                         'uf_privacy':'ufv:privacyFlag',
                         'display_name':'rdfs:label',
                         'gatorlink':'ufv:gatorlink'
                         }
    direct_resource_preds = {'homedept_uri':'ufv:homeDept'}
    for key in direct_data_preds:
        if key in person:
            pred = direct_data_preds[key]
            val = person[key]
            ardf = ardf + assert_data_property(person_uri, pred, val)
    for key in direct_resource_preds:
        if key in person:
            pred = direct_resource_preds[key]
            val = person[key]
            ardf = ardf + assert_resource_property(person_uri, pred, val)

    # Add Vcard Assertions

    vcard = {}
    for key in ['last_name', 'first_name', 'middle_name', 'primary_email',
                'name_prefix', 'name_suffix', 'fax', 'phone', 'preferred_title',
                ]:
        vcard[key] = person[key]
    ardf = ardf + add_vcard(person_uri, vcard)

    # Add Position Assertions

    position = {}
    for key in ['start_date', 'description', 'end_date', 'position_depturi',
                'position_type']:
        position[key] = person[key]
    ardf = ardf + add_position(person_uri, position)
    
    return [ardf, person_uri]

def update_person(vivo_person, source_person):
    """
    Given a data structure representing a person in VIVO, and a data
    structure rpesenting the same person with data values from source
    systems, generate the ADD and SUB RDF necessary to update the VIVO
    person's data values to the corresponding values in the source
    """
    ardf = ""
    srdf = ""

    # Update direct assertions

    # Update vcard assertions

    # Update positions and their assertions
    
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
    print json.dumps(source_person, indent=4)
    
    if 'uri' in source_person and source_person['uri'] is not None:
        print >>log_file, "Updating person at", source_person['uri']
##        vivo_person = get_person(source_person['uri'])
##        [add, sub] = update_person(vivo_person, source_person)
##        ardf = ardf + add
##        srdf = srdf + sub
    else:
        print >>log_file, "Adding person", source_person['ufid']
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
