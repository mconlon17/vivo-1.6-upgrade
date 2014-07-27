#!/usr/bin/env/python

"""
    person_ingest.py: Given person data from HR, compare to VIVO and
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
    Handle case 2 -- updating current and UF entity designation -- in a separate
    program

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

from vivofoundation import rdf_header
from vivofoundation import rdf_footer

from vivopeople import get_person
from vivopeople import add_person
from vivopeople import update_person

from datetime import datetime
import codecs
import sys
import os
import json
import vivofoundation as vf

__harvest_text__ = "Python Person Ingest " + __version__
__harvest_time__ = datetime.now().isoformat()

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
    from vivofoundation import read_csv
    from vivofoundation import find_vivo_uri
    from vivofoundation import get_vivo_uri
    from vivofoundation import untag_predicate
    from vivofoundation import comma_space
    from vivopeople import improve_jobcode_description
    from vivopeople import get_position_type
    from vivopeople import repair_phone_number
    from vivopeople import repair_email
    from operator import itemgetter
    
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
        else:   
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
            person['position_orguri'] = depturi
            if depturi is None:
                exc_file.write(ufid+' has deptid ' + position['DEPTID'] +\
                               ' not found.\n')
                anyerrors = True
        else:
            exc_file.write(ufid+' has position in department '+\
                position['DEPTID']+' which is on the department exception '+
                ' list.  No position will be added.\n')
            anyerrors = True
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
            person['privacy_flag'] = privacy[ufid]['UF_PROTECT_FLG']
            if person['privacy_flag'] == 'Y':
                exc_file.write(ufid+' has protect flag Y\n')
                anyerrors = True
        if ufid not in contact:
            exc_file.write(ufid+' not found in contact data\n')
            anyerrors = True
        else:
            info = contact[ufid]

            if info['FIRST_NAME'].title() != '':
                person['given_name'] = info['FIRST_NAME'].title()

            if info['LAST_NAME'].title() != '':
                person['family_name'] = info['LAST_NAME'].title()

            if info['MIDDLE_NAME'].title() != '':
                person['additional_name'] = info['MIDDLE_NAME'].title()

            if info['NAME_SUFFIX'].title() != '':
                person['honorific_suffix'] = info['NAME_SUFFIX'].title()

            if info['NAME_PREFIX'].title() != '':
                person['honorific_prefix'] = info['NAME_PREFIX'].title()

            if info['DISPLAY_NAME'] != '':
                person['display_name'] = comma_space(info['DISPLAY_NAME'].\
                                                     title())

            if info['GATORLINK'] != '':
                person['gatorlink'] = info['GATORLINK'].lower()

            if info['WORKINGTITLE'] != '':
                if info['WORKINGTITLE'].upper() == info['WORKINGTITLE']:
                    person['title'] = \
                        improve_jobcode_description(\
                            position['JOBCODE_DESCRIPTION'])
                else:
                    person['preferred_title'] = info['WORKINGTITLE']
                    
            if info['UF_BUSINESS_EMAIL'] != '':
                person['primary_email'] = \
                                        repair_email(info['UF_BUSINESS_EMAIL'])
            if info['UF_BUSINESS_PHONE'] != '':
                person['phone'] = repair_phone_number(info['UF_BUSINESS_PHONE'])
                
            if info['UF_BUSINESS_FAX'] != '':
                person['fax'] = repair_phone_number(info['UF_BUSINESS_FAX'])
                    
            if ok_deptid(info['HOME_DEPT'], deptid_exceptions):
                person['home_deptid'] = info['HOME_DEPT']
                homedept_uri = find_vivo_uri('ufv:deptID', info['HOME_DEPT'])
                person['homedept_uri'] = homedept_uri
                if homedept_uri is None:
                    exc_file.write(ufid + ' has home department deptid '+\
                        info['HOME_DEPT'] + ' not found in VIVO\n')
                    anyerrors = True
            else:
                exc_file.write(ufid+' has home department on exception list.'+\
                    ' This person will not be added to VIVO.\n')
                anyerrors = True

        if position['START_DATE'] != '':
            try:
                person['start_date'] = datetime.strptime(position['START_DATE'],\
                    '%Y-%m-%d')
            except ValueError:
                exc_file.write(ufid + ' invalid start date ' +\
                               position['START_DATE']+'\n')
                anyerrors = True

        if position['END_DATE'] != '':
            try:
                person['end_date'] = datetime.strptime(position['END_DATE'],\
                    '%Y-%m-%d')
            except ValueError:
                exc_file.write(ufid + ' invalid end date ' +\
                               position['END_DATE']+'\n')
                anyerrors = True

        if position['JOBCODE_DESCRIPTION'] != '':            
            person['position_label'] = \
                improve_jobcode_description(position['JOBCODE_DESCRIPTION'])
            if str(person['position_label']) in position_exceptions:
                exc_file.write(ufid+' has position description '+
                    person['position_label'] +\
                    ' found in position exceptions.' +\
                    'The position will not be added.\n')
                anyerrors = True
        person['date_harvested'] = __harvest_time__
        person['harvested_by'] = __harvest_text__
        if not anyerrors:
            people[row] = person
    privacy.close()
    contact.close()
    deptid_exceptions.close()
    ufid_exceptions.close()
    uri_exceptions.close()
    position_exceptions.close()
    return people

# Start here

debug = True
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

    if debug:
        print
        print "Consider"
        print
        view_person = dict(source_person)
        if view_person.get('end_date',None) is not None:
            view_person['end_date'] = view_person['end_date'].isoformat()
        if view_person.get('start_date',None) is not None:
            view_person['start_date'] = view_person['start_date'].isoformat()       
        print json.dumps(view_person, indent=4)
    
    if 'uri' in source_person and source_person['uri'] is not None:
        print >>log_file, "Updating person at", source_person['uri']
        vivo_person = get_person(source_person['uri'])
        [add, sub] = update_person(vivo_person, source_person)
        ardf = ardf + add
        srdf = srdf + sub
    else:
        print >>log_file, "Adding person", source_person['ufid']
        [add, person_uri] = add_person(source_person)
        ardf = ardf + add

adrf = ardf + rdf_footer()
srdf = srdf + rdf_footer()
add_file.write(adrf)
sub_file.write(srdf)
add_file.close()
sub_file.close()
exc_file.close()
print >>log_file, datetime.now(), "Finished"
