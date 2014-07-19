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

    Version 0.0 MC 2013-04-06
     -- Read HR data and UFID person data from VIVO.  Compare. Identify and
        tabulate cases
    Version 0.1 MC 2013-05-28
     -- Add exception processing for departments, ufids, position_type and
        position_description
     -- Add add_person
     -- Add former_person to remove assertions for people who have left the
        university
     -- Add current_person to assert UFEntity and UFCurrentEntity for people
        who are currently employed
     -- Add sampling of case processing for testing purposes
     -- Added add_position for case 1
     Version 0.2 MC 2013-06-18
     -- Reads five files -- privacy, HR, contact, deptid exceptions, ufid
        exceptions.  Writes four files -- log, exception list, addition RDF and
        subtraction RDF
     -- Adds contact info for people being created
     -- For case 2 update position end date for people who have left
     -- For case 3, update the contact info including home department
     -- For case 3, update position info, including adding position if necessary
     Version 0.3 MC 2013-07-24
     -- Correct errors in ontology names
     -- Improve datetime handling
     -- Improve filtering of source data for start and end dates
     -- Improve phone number handling
     -- XML escape all output to RDF
     Version 0.4 MC 2013-08-05
     -- Catch deptid exception for update_position
     -- merged with forked version that fixed resource type assertions
     Version 0.5 cpb@ufl.edu 2013-08-05
     -- merged with forked version form succes run that fixed resource type
        assertions
     -- fixed core and other resource namespace issues
     Version 0.6 MC 2013-08-07
     -- Fix classification error for Case 1/2 determination
     -- Read new format for privacy_data
     Version 0.7 MC 2013-08-11
     -- ok_privacy writes exceptions to exception file and returns False
        rather than throwing an exception
     -- Read privacy data as a CSV
     -- map contact data elements from UF names to VIVO names
     -- improvements in position and working titles
     -- improvements in wording of exception output
     Version 0.8 MC 2013-08-26
     -- Only edit the UF working title if it is all upper case
     -- Add a space after the comma in the display name if needed
     -- Handle additional abbreviations in position and working titles
     -- Case 2 now removes preferred titles correctly
     -- Improve run time by improving contact data only if we are going
        to use it.  So we improve 40,000 instead of 2M
     -- Improve run time by using action report to reduce the size of privacy
        and contact dictionaries
     -- Fix bug in add regarding start dates
     -- For case 1, show the person URI in the log when added
     -- Improved indenting in RDF for add person
     -- For case 3, check for qualified positions before adding them
     -- Handle multiple commas in positiona and working titles
     -- Fix bug that wrote position_uri to sub.rdf
     -- Review and improve exception handling
     -- Improvements in log formatting
     -- Fix bug in recognizing that a person already has a valid home department
     Version 0.9 MC 2013-09-04
     -- Improvements in EXC file formatting
     -- Improvements in LOG file formatting
     -- Every print statement now explictly routed to one of the output files
     -- Version numbers of person-ingest and vivotools now printed in the log
     -- UFIDs now processed in order -- aids in reading logs and restarts
     -- Fix bug in case 1 counting
     -- Fix bug in update_contact for preferred_title
     -- Fixed bugs in escaping output
     Version 0.91 MC 2013-09-08
     -- Add URI exception list for people with UFID, but who are not on the UF
        pay list.  Anyone on the URI exception list will not be processed at
        all. They are, in effect, manual edit only.  Because they have a UFID,
        they will accumulate other facts -- grants, courses.  If they are
        manually edited to include UFEntity, they will have papers added as
        well.
     -- Remove all references to homeDeptFor.  This will be added by the
        inferencer as an inverse property to homeDept
     Version 0.92 MC 2013-09-08
     -- URI Exception list handling added to case 3
     Version 0.93 MC 2013-10-03
     -- Added foaf:Person assertion to add_person
     Version 0.94 MC 2013-10-05
     -- Check for ok_position to see if position should be added (case 1 and
        case 3).  We only add HR positions, not the "positions" from course
        ingest (HR_POSITION=0) which are used to add new people.  We do not
        add positions to excluded departments.
    Version 0.95 MC 2013-10-17
     -- Add Ops Lump Sum Payment to list of excluded position titles
    Version 0.96 MC 2013-12-11
     -- Correct support for adding people without positions
    Version 0.97 MC 2013-12-16
     -- Support adding people without home departments
    Version 0.98 MC 2014-02-24
    --  Fix email addresses on the way in

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
__version__ = "0.98"

from datetime import datetime
# import dateutil.parser
import re
import os
import sys
import pickle
import random # for testing purposes, select subsets of records to process
import tempita
import vivotools as vt
from xml.sax.saxutils import escape

class DeptIDNotInVIVOException(Exception):
    """
    DeptIDNotInVIVOException should be thrown if an attempt is made to connect
    a person to a department whose DeptID is not in VIVO.  person-ingest
    does not create departments.  The exception can be handled by a data
    manager who assigns the deptid to an existing department, or adds
    a department as necessary.
    """
    pass

class UFIDNotInPrivacyDataException(Exception):
    """
    Every UFID from HR is checked against the privacy data.  If it can not be
    this exception is thrown.
    """
    pass

def make_position_type(salary_plan):
    """
    Given a salary plan code, map to one of the VIVO position types
    """
    position_dict = {
        'CPFI':	'postdoc',
        'CTSY':	'courtesy-faculty',
        'FA09':	'faculty',
        'FA9M': 'clinical-faculty',
        'FA10':	'faculty',
        'FA12':	'faculty',
        'FACM':	'clinical-faculty',
        'FAPD':	'postdoc',
        'FASU':	'faculty',
        'FELL':	None, # Fellowship, lump sum payment only
        'FWSP':	None, # student-assistant
        'GA09':	None, # graduate-assistant
        'GA12':	None, # graduate-assistant
        'GASU':	None, # graduate-assistant
        'HOUS':	'housestaff',
        'ISCR':	None, # Scholarship, lump sum payment only
        'OF09':	'temp-faculty',
        'OF12':	'temp-faculty',
        'OFSU':	'temp-faculty',
        'OPSE': None, # OPS
        'OPSN': None, # OPS
        'STAS':	None, # student-assistant
        'STBW':	None, # student-assistant
        'TA09':	'non-academic',
        'TA10':	'non-academic',
        'TA12':	'non-academic',
        'TASU': 'non-academic',
        'TU1E':	'non-academic',
        'TU2E': 'non-academic',
        'TU9E':	'non-academic',
        'TUSE':	'non-academic',
        'TU1N':	None, # TEAMS Hourly
        'TU2N':	None, # TEAMS Hourly
        'TU9N':	None, # TEAMS Hourly
        'TUSN':	None, # TEAMS Hourly
        'US1N':	None, # USPS
        'US2N':	None, # USPS
        'US9N':	None, # USPS
        'USSN':	None, # USPS
        'US2E': 'non-academic', # USPS Exempt
        }
    position_type = position_dict.get(salary_plan, None)
    return position_type

def make_position_title(s):
    """
    HR uses a series of abbreviations to fit job titles into limited text
    strings.
    Here we attempt to reverse the process -- a short title is turned into a
    longer one
    """
    if s == "":
        return s
    if s[len(s)-1] == ',':
        s = s[0:len(s)-1]
    if s[len(s)-1] == ',':
        s = s[0:len(s)-1]
    s = s.lower()
    s = s.title()
    s = s + ' '   # so we can find throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace(" & ", " and ")
    t = t.replace(" &", " and ")
    t = t.replace("&", " and ")
    t = t.replace("/", " @")
    t = t.replace("/", " @") # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace(",", " !") # might be two commas in input
    t = t.replace("-", " #")
    t = t.replace("Aca ", "Academic ")
    t = t.replace("Acad ", "Academic ")
    t = t.replace("Act ", "Acting ")
    t = t.replace("Advanc ", "Advanced ")
    t = t.replace("Adv ", "Advisory ")
    t = t.replace("Alumn Aff ", "Alumni Affairs ")
    t = t.replace("Ast #R ", "Research Assistant ")
    t = t.replace("Ast #G ", "Grading Assistant ")
    t = t.replace("Ast #T ", "Teaching Assistant ")
    t = t.replace("Ast ", "Assistant ")
    t = t.replace("Affl ", "Affiliate ")
    t = t.replace("Aso ", "Associate ")
    t = t.replace("Asoc ", "Associate ")
    t = t.replace("Assoc ", "Associate ")
    t = t.replace("Prof ", "Professor ")
    t = t.replace("Mstr ", "Master ")
    t = t.replace("Couns ", "Counselor ")
    t = t.replace("Adj ", "Adjunct ")
    t = t.replace("Dist ", "Distinguished ")
    t = t.replace("Cio ", "Chief Information Officer ")
    t = t.replace("Coo ", "Chief Operating Officer ")
    t = t.replace("Co ", "Courtesy ")
    t = t.replace("Clin ", "Clinical ")
    t = t.replace("Finan ", "Financial ")
    t = t.replace("Grad ", "Graduate ")
    t = t.replace("Hou ", "Housing ")
    t = t.replace("Stu ", "Student ")
    t = t.replace("Prg ", "Programs ")
    t = t.replace("Dev ", "Development ")
    t = t.replace("Aff ", "Affiliate ")
    t = t.replace("Svc ", "Services ")
    t = t.replace("Svcs ", "Services ")
    t = t.replace("Devel ", "Development ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Progs ", "Programs ")
    t = t.replace("Facil ", "Facility ")
    t = t.replace("Hlth ", "Health ")
    t = t.replace("Ifas ", "IFAS ")
    t = t.replace("Int ", "Interim ")
    t = t.replace("Sctst ", "Scientist ")
    t = t.replace("Supp ", "Support ")
    t = t.replace("Cty ", "County ")
    t = t.replace("Ext ", "Extension ")
    t = t.replace("Emer ", "Emeritus ")
    t = t.replace("Enforce ", "Enforcement ")
    t = t.replace("Environ ", "Environmental ")
    t = t.replace("Gen ", "General ")
    t = t.replace("Jnt ", "Joint ")
    t = t.replace("Eng ", "Engineer ")
    t = t.replace("Ctr ", "Center ")
    t = t.replace("Opr ", "Operator ")
    t = t.replace("Admin ", "Administrative ")
    t = t.replace("Dis ", "Distinguished ")
    t = t.replace("Ser ", "Service ")
    t = t.replace("Rep ", "Representative ")
    t = t.replace("Radiol ", "Radiology ")
    t = t.replace("Technol ", "Technologist ")
    t = t.replace("Pres ", "President ")
    t = t.replace("Pres5 ", "President 5 ")
    t = t.replace("Pres6 ", "President 6 ")
    t = t.replace("Emin ", "Eminent ")
    t = t.replace("Cfo ", "Chief Financial Officer ")
    t = t.replace("Prov ", "Provisional ")
    t = t.replace("Adm ", "Administrator ")
    t = t.replace("Info ", "Information ")
    t = t.replace("It ", "Information Technology ")
    t = t.replace("Mgr ", "Manager ")
    t = t.replace("Mgt ", "Management ")
    t = t.replace("Vis ", "Visiting ")
    t = t.replace("Phas ", "Phased ")
    t = t.replace("Prog ", "Programmer ")
    t = t.replace("Pract ", "Practitioner ")
    t = t.replace("Registr ", "Registration ")
    t = t.replace("Rsch ", "Research ")
    t = t.replace("Ret ", "Retirement ")
    t = t.replace("Sch ", "School ")
    t = t.replace("Tch ", "Teaching ")
    t = t.replace("Tv ", "TV ")
    t = t.replace("Univ ", "University ")
    t = t.replace("Educ ", "Education ")
    t = t.replace("Crd ", "Coordinator ")
    t = t.replace("Res ", "Research ")
    t = t.replace("Dir ", "Director ")
    t = t.replace("Pky ", "PK Yonge ")
    t = t.replace("Rcv ", "Receiving ")
    t = t.replace("Sr ", "Senior ")
    t = t.replace("Spec ", "Specialist ")
    t = t.replace("Spv ", "Supervisor ")
    t = t.replace("Supv ", "Supervisor ")
    t = t.replace("Supt ", "Superintendant ")
    t = t.replace("Pky ", "P. K. Yonge ")
    t = t.replace("Ii ", "II ")
    t = t.replace("Iii ", "III ")
    t = t.replace("Iv ", "IV ")
    t = t.replace("Communic ", "Communications ")
    t = t.replace("Postdoc ", "Postdoctoral ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Uf ", "UF ")
    t = t.replace("Ufrf ", "UFRF ")
    t = t.replace("Vp ", "Vice President ")
    t = t.replace(" @", "/") # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" #", "-") # restore -
    return t[:-1] # Take off the trailing space

def add_position(data):
    """
    Given a dictionary of values for creating a position, create a call
    to make_position_rdf to create the rdf and return the rdf and position_uri
    """
    person_uri = data['person_uri']
    org_uri = data['org_uri']
    title = data['hr_title']
    position_label = data['position_label']
    position_type = data['position_type']
    start_date = data['START_DATE']
    end_date = data['END_DATE']
    return make_position_rdf(person_uri, org_uri, title, position_label,
                             position_type, start_date, end_date)

def make_person_in_position_rdf(person_uri, position_uri):
    """
    Given a URI for a person and URI for a position, make RDF for the
    personInPosition assertion
    """
    person_in_position_template = tempita.Template("""
    <rdf:Description rdf:about="{{person_uri}}">
        <vivo:personInPosition rdf:resource="{{position_uri}}"/>
    </rdf:Description>
    """)
    rdf = ""
    rdf = person_in_position_template.substitute(person_uri=person_uri,
            position_uri=position_uri)
    return rdf

def make_organization_for_position_rdf(org_uri, position_uri):
    """
    Given a URI for an Org and URI for a position, make RDF for the
    organization for position assertion
    """
    organization_for_position_template = tempita.Template("""
    <rdf:Description rdf:about="{{org_uri}}">
        <vivo:organizationForPosition rdf:resource="{{position_uri}}"/>
    </rdf:Description>
    """)
    rdf = ""
    rdf = organization_for_position_template.substitute(org_uri=org_uri,
            position_uri=position_uri)
    return rdf

def make_position_rdf(person_uri, org_uri, title, position_label, position_type,
                      start_date, end_date):
    """
    Given position values, make the RDF for the position and time interval,
    and the associated facts for linking the position to the person, the org
    and the time interval
    """
    position_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{position_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Position"/>
        <vivo:dateTimeInterval rdf:resource="{{datetime_interval_uri}}"/>
        <vivo:positionForPerson rdf:resource="{{person_uri}}"/>
        <vivo:positionInOrganization rdf:resource="{{org_uri}}"/>
        {{if position_type=="non-faculty"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Non-FacultyAcademicPosition"/>
        {{endif}}
        {{if position_type=="clinical-faculty"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#FacultyPosition"/>
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/ClinicalFacultyPosition"/>
        {{endif}}
        {{if position_type=="faculty"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#FacultyPosition"/>
        {{endif}}
        {{if position_type=="courtesy-faculty"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#FacultyPosition"/>
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/CourtesyFacultyPosition"/>
        {{endif}}
        {{if position_type=="postdoc"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#FacultyPosition"/>
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/PostDocPosition"/>
        {{endif}}
        {{if position_type=="librarian"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#LibrarianPosition"/>
        {{endif}}
        {{if position_type=="non-academic"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Non-AcademicPosition"/>
        {{endif}}
        {{if position_type=="student-assistant"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Non-AcademicPosition"/>
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/StudentAssistant"/>
        {{endif}}
        {{if position_type=="graduate-assistant"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Non-FacultyAcademicPosition"/>
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/GraduateAssistant"/>
        {{endif}}
        {{if position_type=="housestaff"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Non-FacultyAcademicPosition"/>
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/Housestaff"/>
        {{endif}}
        {{if position_type=="temp-faculty"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#FacultyPosition"/>
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/TemporaryFaculty"/>
        {{endif}}
        {{if position_type=="faculty-administrative"}}
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#FacultyAdministrativePosition"/>
        {{endif}}
        <vivo:hrJobTitle>{{title}}</vivo:hrJobTitle>
        <rdfs:label>{{position_label}}</rdfs:label>
        <ufVivo:harvestedBy>Python People version 1.0</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>""")
    rdf = ""
    [datetime_interval_rdf, datetime_interval_uri] = \
        vt.make_datetime_interval_rdf(start_date, end_date)

    position_uri = vt.get_vivo_uri()
    harvest_datetime = vt.make_harvest_datetime()
    rdf = rdf + datetime_interval_rdf
    rdf = rdf + make_person_in_position_rdf(person_uri, position_uri)
    rdf = rdf + make_organization_for_position_rdf(org_uri, position_uri)
    rdf = rdf + position_rdf_template.substitute(position_uri=position_uri,
        person_uri=person_uri, datetime_interval_uri=datetime_interval_uri,
        org_uri=org_uri, position_type=position_type, title=escape(title),
        position_label=escape(position_label),
        harvest_datetime=harvest_datetime)
    return [rdf, position_uri]

def ok_deptid(deptid):
    """
    Some deptids are in an exception dictionary of patterns.  If a person is
    in one of these departments, they will not be listed in VIVO.

    Deptids in the exception dictionary are regular expressions

    Given a dept id, the deptid exception list is checked.  True is
    returned if the deptid is not matched.  False is returned
    if the deptid is matched.
    """
    ok = True
    for pattern_string in deptid_exception_dictionary.keys():
        pattern = re.compile(pattern_string)
        if pattern.search(deptid) is not None:
            ok = False
            break
    return ok

def ok_ufid(ufid):
    """
    Some ufids are in an exception dictionary (test accounts, for example).
    If a person has a UFID in the exception dictionary, they will not be
    listed in VIVO.

    Given a ufid, the exception dictionary is checked.  True is
    returned if the ufid is not matched.  False is returned
    if the ufid is matched.
    """
    if ufid not in ufid_exception_dictionary:
        return True
    else:
        return False

def ok_position(data):
    """
    Given a person's data, determine if the position can be added
    """
    if data['HR_POSITION'] == "0":
        return False
    else:
        return True

def ok_position_title(position_title):
    """
    Some position titles are on an exception list.
    If a person has a position title on the exception list, they will not be
    listed in VIVO.

    If the position_title is on the exception list, return False (not OK!)
    """
    position_title_exception_list = \
        ["Academic Lump Sum Payment", "Ops Lump Sum Payment"]
    if position_title not in position_title_exception_list:
        return True
    else:
        return False

def ok_privacy(ufid):
    """
    We do not add people to VIVO who have their UF_PROTECT_FLAG set to
    yes.  If the ufid is not found in the privacy data, indicate in the
    exception file, and not OK
    """
    try:
        if privacy_dictionary[ufid]['uf_security_flag'] == 'Y' or\
           privacy_dictionary[ufid]['uf_protect_flag'] == 'Y':
            return False
        else:
            return True
    except:
        print >>exc_file, ufid, "not found in privacy data"
        return False

def make_privacy_dictionary(filename, action_report, debug=False):
    """
    Read a CSV file of privacy records from UF.
    """
    if os.path.isfile('privacy_data.pcl'):
        privacy_dictionary = pickle.load(open('privacy_data.pcl', 'r'))
        return privacy_dictionary
    privacy_dictionary = {}
    privacy_data = vt.read_csv(filename)
    if debug:
        print >>log_file, datetime.now(), "Privacy Data has",\
            len(privacy_data), "rows"
        print >>log_file, datetime.now(), "First row", privacy_data[1]
    i = 0
    for row in privacy_data.keys():
        i = i + 1
        ufid = privacy_data[row]['UFID']
        if ufid in action_report:
            uf_security_flag = privacy_data[row]['UF_SECURITY_FLG']
            uf_protect_flag = privacy_data[row]['UF_PROTECT_FLG']
            uf_publish_flag = privacy_data[row]['UF_PUBLISH_FLG']
            privacy_dictionary[ufid] = {'uf_security_flag':uf_security_flag,
                                        'uf_protect_flag':uf_protect_flag,
                                        'uf_publish_flag':uf_publish_flag}
        if debug and i % 10000 == 0:
            print >>log_file, i, ".",
    if debug:
        print >>log_file
    if debug:
        ntot = 0
        nsec = 0
        npro = 0
        npub = 0
        for ufid in privacy_dictionary.keys():
            ntot = ntot + 1
            if privacy_dictionary[ufid]['uf_security_flag'] == 'Y':
                nsec = nsec + 1
            if privacy_dictionary[ufid]['uf_protect_flag'] == 'Y':
                npro = npro + 1
            if privacy_dictionary[ufid]['uf_publish_flag'] == 'Y':
                npub = npub + 1
        print >>log_file, "Total entries in privacy dictionary is", ntot
        print >>log_file, "Number of UF_SECURITY_FLAG == 'Y'   is", nsec
        print >>log_file, "Number of UF_PROTECT_FLAG == 'Y'    is", npro
        print >>log_file, "Number of UF_PUBLISH_FLAG == 'Y'    is", npub
    pickle.dump(privacy_dictionary, open('privacy_data.pcl', 'w'))
    return privacy_dictionary

def fix_email(email, exp = re.compile(r'\w+\.*\w+@\w+\.(\w+\.*)*\w+')):
    """
    Given an email string, fix it
    """
    s = exp.search(email)
    if s is None:
        return ""
    elif s.group() is not None:
        return s.group()
    else:
        return ""

def improve_contact_data(data):
    """
    given contact data as it comes from UF, attempt to improve it by
    improving attribute names, repairing phone numbers, improving display
    names and working titles
    """

    if data['WORKINGTITLE'].upper() == data['WORKINGTITLE']:

        # if UF Contact data working title is all upper case, we
        # attempt to improve it

        wt = make_position_title(data['WORKINGTITLE'])
        data['preferred_title'] = wt
    else:

        # if UF contact data has a mixed case working title, we assume
        # it has been hand edited in the source system and we leave it
        # untouched

        data['preferred_title'] = data['WORKINGTITLE']
    del data['WORKINGTITLE']

    data['fax_number'] = \
        vt.repair_phone_number(data['UF_BUSINESS_FAX'])
    del data['UF_BUSINESS_FAX']

    data['primary_phone_number'] = \
        vt.repair_phone_number(data['UF_BUSINESS_PHONE'])
    del data['UF_BUSINESS_PHONE']

    data['display_name'] = \
        data['DISPLAY_NAME'].title()
    k = data['display_name'].find(',')
    if k > -1 and data['display_name'][k+1] != " ":
        data['display_name'] = \
            data['display_name'][0:k] + ', ' + data['display_name'][k+1:]
    del data['DISPLAY_NAME']

    if data['HOME_DEPT'] != '':
        data['home_deptid'] = data['HOME_DEPT'].rjust(8, '0')
        del data['HOME_DEPT']

    data['first_name'] = data['FIRST_NAME']
    del data['FIRST_NAME']

    data['last_name'] = data['LAST_NAME']
    del data['LAST_NAME']

    data['middle_name'] = data['MIDDLE_NAME']
    del data['MIDDLE_NAME']

    data['name_prefix'] = data['NAME_PREFIX']
    del data['NAME_PREFIX']

    data['name_suffix'] = data['NAME_SUFFIX']
    del data['NAME_SUFFIX']

    data['gatorlink'] = data['GATORLINK']
    del data['GATORLINK']

    data['primary_email'] = fix_email(data['UF_BUSINESS_EMAIL'])
    del data['UF_BUSINESS_EMAIL']

    return data


def make_contact_dictionary(filename, action_report, debug=False):
    """
    Read a CSV file with Contact data.  Create a dictionary with one entry
    per UFID.

    If multiple rows exist in the contact data for a particular UFID, the last
    row will be used in the dictionary
    """
    if os.path.isfile('contact_data.pcl'):
        contact_dictionary = pickle.load(open('contact_data.pcl', 'r'))
        return contact_dictionary
    contact_dictionary = {}
    contact_data = vt.read_csv(filename)
    if debug:
        print >>log_file, datetime.now(), "Contact Data has",\
            len(contact_data), "rows"
        print >>log_file, datetime.now(), "First row", contact_data[1]
    for row in contact_data.keys():
        if debug:
            if row % 10000 == 0:
                print >>log_file, row,
        ufid = contact_data[row]['UFID']

        # for ufid we will process (HR, VIVO or both),
        # assign the data to an entry in the dictionary keyed by ufid

        if ufid in action_report:
            data = improve_contact_data(contact_data[row])
            contact_dictionary[ufid] = data
    if debug:
        print >>log_file
    pickle.dump(contact_dictionary, open('contact_data.pcl', 'w'))
    return contact_dictionary

def make_uri_exception_dictionary(filename="uri_exceptions.csv", debug=False):
    """
    Read a CSV file with URI Exception data.  Create a dictionary with one entry
    per UFID.  Exception data has two elements -- a URI and a Comment
    (often their name) indicating why the URI is on the exception list.

    If multiple rows exist in the exception data for a particular UFID, the last
    row will be used in the dictionary
    """
    uri_exception_dictionary = {}
    uri_exception_data = vt.read_csv(filename)
    for row in uri_exception_data.keys():
        uri = uri_exception_data[row]['uri']
        uri_exception_dictionary[uri] = uri_exception_data[row]
    return uri_exception_dictionary

def make_ufid_exception_dictionary(filename="ufid_exceptions.csv", debug=False):
    """
    Read a CSV file with UFID Exception data.  Create a dictionary with one
    entry per UFID.  Exception data has two elements -- a UFID and a Comment
    indicating why the UFID is on the exception list.

    If multiple rows exist in the exception data for a particular UFID, the last
    row will be used in the dictionary
    """
    ufid_exception_dictionary = {}
    ufid_exception_data = vt.read_csv(filename)
    for row in ufid_exception_data.keys():
        ufid = ufid_exception_data[row]['ufid']
        ufid_exception_dictionary[ufid] = ufid_exception_data[row]
    return ufid_exception_dictionary

def make_deptid_exception_dictionary(filename="deptid_exceptions.csv",
                                     debug=False):
    """
    Read a CSV file with DEPTID Exception patterns.  Create a dictionary with
    one entry per pattern.  Exception data has two elements: 1) a regular
    expression indicating people with home deptids matching the regular
    expression should be excluded from VIVO, and 2) a comment indicating why
    the pattern is an exception.

    If multiple rows exist in the contact data for a particular pattern, the
    last row will be used in the dictionary
    """
    deptid_exception_dictionary = {}
    deptid_exception_data = vt.read_csv(filename)
    for row in deptid_exception_data.keys():
        deptid_pattern = deptid_exception_data[row]['deptid_pattern']
        deptid_exception_dictionary[deptid_pattern] = deptid_exception_data[row]
    return deptid_exception_dictionary

def make_hr_dictionary(filename="position_data.csv", debug=False):
    """
    Read a CSV file with HR data.  Create a dictionary with one entry
    per UFID.  Apply inclusion and exclusion criteria so that the
    resulting dictionary contains exactly the people who should be marked
    as current in UF VIVO.

    If multiple rows exist in the HR data for a particular UFID, the last
    row will be used in the dictionary
    """
    hr_dictionary = {}
    position_type_count = {}
    hr_data = vt.read_csv(filename)
    for row in hr_data.keys():
        ufid = hr_data[row]['UFID']
        deptid = hr_data[row]['DEPTID']

        # Improve the data

        position_type = make_position_type(hr_data[row]['SAL_ADMIN_PLAN'])
        position_label = \
            make_position_title(hr_data[row]['JOBCODE_DESCRIPTION'])
        hr_data[row]['position_type'] = position_type
        hr_data[row]['position_label'] = position_label
        if hr_data[row]['START_DATE'] != '':
            hr_data[row]['START_DATE'] = \
            datetime.strptime(hr_data[row]['START_DATE'],
                              "%Y-%m-%d").isoformat()
        if hr_data[row]['END_DATE'] != '':
            hr_data[row]['END_DATE'] = \
            datetime.strptime(hr_data[row]['END_DATE'],
                              "%Y-%m-%d").isoformat()
        hr_data[row]['hr_title'] = \
            hr_data[row]['JOBCODE_DESCRIPTION']
        hr_dictionary[ufid] = hr_data[row]


    if debug:
        for ufid in hr_dictionary.keys():
            position_type = hr_dictionary[ufid]['position_type']
            position_type_count[position_type] = \
                position_type_count.get(position_type, 0) + 1
        for position_type in sorted(position_type_count.keys()):
            print >>log_file, position_type, position_type_count[position_type]

    return hr_dictionary

def add_person(data):
    """
    Given data for a person, generate the addition RDF to add the person to
    VIVO, along with the URI of the new person
    """
    person_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFEntity"/>
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFCurrentEntity"/>
        <ufVivo:ufid>{{ufid}}</ufVivo:ufid>
        {{if position_type == "faculty"}}
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#FacultyMember"/>
        {{endif}}
        {{if position_type == "postdoc"}}
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Postdoc"/>
        {{endif}}
        {{if position_type == "courtesy-faculty"}}
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/CourtesyFaculty"/>
        {{endif}}
        {{if position_type == "clinical-faculty"}}
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/ClinicalFaculty"/>
        {{endif}}
        {{if position_type == "housestaff"}}
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/Housestaff"/>
        {{endif}}
        {{if position_type == "temp-faculty"}}
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/TemporaryFaculty"/>
        {{endif}}
        {{if position_type == "non-academic"}}
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#NonAcademic"/>
        {{endif}}
        {{if len(display_name) > 0}}
        <rdfs:label>{{display_name}}</rdfs:label>
        {{endif}}
        {{if len(last_name) > 0}}
        <foaf:lastName>{{last_name}}</foaf:lastName>
        {{endif}}
        {{if len(first_name) > 0}}
        <foaf:firstName>{{first_name}}</foaf:firstName>
        {{endif}}
        {{if len(middle_name) > 0}}
        <vivo:middleName>{{middle_name}}</vivo:middleName>
        {{endif}}
        {{if len(prefix_name) > 0}}
        <bibo:prefixName>{{prefix_name}}</bibo:prefixName>
        {{endif}}
        {{if len(suffix_name) > 0}}
        <bibo:suffixName>{{suffix_name}}</bibo:suffixName>
        {{endif}}
        {{if len(preferred_title) > 0}}
        <vivo:preferredTitle>{{preferred_title}}</vivo:preferredTitle>
        {{endif}}
        {{if len(gatorlink) > 0}}
        <ufVivo:gatorlink>{{gatorlink}}</ufVivo:gatorlink>
        {{endif}}
        {{if len(primary_email) > 0}}
        <vivo:primaryEmail>{{primary_email}}</vivo:primaryEmail>
        {{endif}}
        {{if len(primary_phone_number) > 0}}
        <vivo:primaryPhoneNumber>{{primary_phone_number}}</vivo:primaryPhoneNumber>
        {{endif}}
        {{if len(fax_number) > 0}}
        <vivo:faxNumber>{{fax_number}}</vivo:faxNumber>
        {{endif}}
        {{if len(duri) > 0}}
        <ufVivo:homeDept rdf:resource="{{duri}}"/>
        {{endif}}
        <ufVivo:harvestedBy>Python People version 1.0</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)
    uri = vt.get_vivo_uri()
    harvest_datetime = vt.make_harvest_datetime()

    if 'display_name' in data:
        display_name = data['display_name']
    else:
        display_name = ""
    if 'last_name' in data:
        last_name = data['last_name']
    else:
        last_name = ""
    if 'first_name' in data:
        first_name = data['first_name']
    else:
        first_name = ""
    if 'middle_name' in data:
        middle_name = data['middle_name']
    else:
        middle_name = ""
    position_type = data['position_type']
    if position_type is None:
        position_type = ""
    ufid = data['UFID']
    if 'duri' in data:
        duri = data['duri']
    else:
        duri = ""
    if 'gatorlink' in data:
        gatorlink = data['gatorlink']
    else:
        gatorlink = ""
    if 'primary_email' in data:
        primary_email = data['primary_email']
    else:
        primary_email = ""
    if 'primary_phone_number' in data:
        primary_phone_number = data['primary_phone_number']
    else:
        primary_phone_number = ""
    if 'fax_number' in data:
        fax_number = data['fax_number']
    else:
        fax_number = ""
    if 'prefix_name' in data:
        prefix_name = data['prefix_name']
    else:
        prefix_name = ""
    if 'suffix_name' in data:
        suffix_name = data['suffix_name']
    else:
        suffix_name = ""
    if 'preferred_title' in data:
        preferred_title = data['preferred_title']
    else:
        preferred_title = ""
    rdf = "\n<!-- Person RDF for " + ufid + " -->"
    rdf = rdf + person_template.substitute(uri=uri,
                        display_name=escape(display_name),
                        last_name=last_name,
                        first_name=first_name,
                        middle_name=middle_name,
                        position_type=position_type,
                        prefix_name=prefix_name,
                        suffix_name=suffix_name,
                        preferred_title=escape(preferred_title),
                        ufid=ufid,
                        gatorlink=gatorlink,
                        primary_email=primary_email,
                        primary_phone_number=primary_phone_number,
                        fax_number=fax_number,
                        duri=duri,
                        harvest_datetime=harvest_datetime)
    return [rdf, uri]

def update_position(person_uri, hr_data):
    """
    Given a person URI and data about the person, update the person's position
    info.  Return addition and substraction RDF.

    """
    ardf = ""
    srdf = ""
    person = vt.get_person(person_uri, get_positions=True)
    try:
        hr_data['org_uri'] = deptid_dictionary[hr_data['DEPTID']]
    except:
        raise DeptIDNotInVIVOException(hr_data['DEPTID'])
        return ["", ""]

    # Loop over the positions.  If the HR position matches, update position

    match = False
    for position in person['positions']:
        if position.get('org_uri', None) == hr_data['org_uri'] and \
           position.get('hr_title', None) == hr_data['hr_title']:
            match = True

            # update is a no-op

            break

    # if the HR position does not match and its a qualified position, add it

    if match == False and ok_position_title(hr_data['position_label']) and \
        ok_position(hr_data) and ok_deptid(hr_data['DEPTID']):
        hr_data['person_uri'] = person_uri
        [add, position_uri] = add_position(hr_data)
        ardf = ardf + add
        print >>log_file, " Added position to VIVO for ", person_uri
    else:
        print >>log_file, " No position added for", person_uri

    return [ardf, srdf]

def assert_end_date_for_position(position_uri, datetime, datetime_precision):
    """
    Given a position uri, a datetime and a datetime precision, assert that the
    position has an end date with the specified precision.  The position has a
    datetime interval which has start and end datetime values.  The end
    datetime value needs to be updated.
    """
    update_end_date_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <core:end rdf:resource="{{end_uri}}"/>
    </rdf:Description>
    """)
    update_position_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <core:dateTimeInterval rdf:resource="{{dt_uri}}"/>
    </rdf:Description>
    """)
    ardf = ""

    # Get the position and its datetime interval uri

    position = vt.get_position(position_uri)
    if 'datetime_interval' in position:
        datetime_interval_uri = \
            position['datetime_interval']['datetime_interval_uri']

        # Create the RDF for a new end date datetime value

        [add, end_date_uri] = vt.make_datetime_rdf(datetime.isoformat(),
            precision=datetime_precision)
        ardf = ardf + add

        # Create the assertion that the datetime interval has the new end date

        add = update_end_date_template.substitute(uri=datetime_interval_uri,
                                                  end_uri=end_date_uri)
        ardf = ardf + add
        return ardf
    else:

        # The position did not have a datetime_interval.  Create one. Assert the
        # position has the datetime interval

        [ardf, dt_uri] = vt.make_datetime_interval_rdf(None,
                                                       datetime.isoformat())
        add = update_position_template.substitute(uri=position['position_uri'],
                                                  dt_uri=dt_uri)
        ardf = ardf + add

        return ardf

def former_person(uri):
    """
    Given a person URI, set values related to leaving the university:
    -- remove UFCurrentEntity (UFEntity will remain)
    -- remove phone
    -- remove email
    -- remove fax number
    -- remove working title
    -- set end date on positions without end dates
    """
    former_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFCurrentEntity"/>
        {{if len(primary_phone_number) > 0}}
            <vivo:primaryPhoneNumber>{{primary_phone_number}}</vivo:primaryPhoneNumber>
        {{endif}}
        {{if len(primary_email) > 0}}
            <vivo:primaryEmail>{{primary_email}}</vivo:primaryEmail>
        {{endif}}
        {{if len(fax_number) > 0}}
            <vivo:faxNumber>{{fax_number}}</vivo:faxNumber>
        {{endif}}
        {{if len(preferred_title) > 0}}
            <vivo:preferredTitle>{{preferred_title}}</vivo:preferredTitle>
        {{endif}}
    </rdf:Description>
    """)
    person = vt.get_person(uri, get_positions=True)
    if 'primary_phone_number' in person:
        primary_phone_number = person['primary_phone_number']
    else:
        primary_phone_number = ""
    if 'primary_email' in person:
        primary_email = person['primary_email']
    else:
        primary_email = ""
    if 'fax_number' in person:
        fax_number = person['fax_number']
    else:
        fax_number = ""
    if 'preferred_title' in person:
        preferred_title = person['preferred_title']
    else:
        preferred_title = ""
    add = ""
    sub = former_template.substitute(uri=uri,
        primary_phone_number=primary_phone_number,
        primary_email=primary_email,
        fax_number=fax_number,
        preferred_title=escape(preferred_title))

    # Add an end date for any position that does not have one.  They all close
    # now with year precision.  Would be better to close positions with
    # explicit HR data regarding end dates

    for position in person['positions']:
        if 'end_date' not in position:
            add = add + assert_end_date_for_position(position['position_uri'],
                                                     datetime.now(), "year")
    return [add, sub]

def current_person(uri):
    """
    Given a person URI mark the person as a current UF person

    Note:  CurrentPerson is a positive assertion.  If the person is
    already a CurrentPerson and we add RDF to assert CurrentPerson, the result
    is redundant RDF which is ignored.  If the person has no CurrentPerson
    assertion, then the assertion goes in place and the person is now known to
    be a CurrentPerson.
    """
    current_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFEntity"/>
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFCurrentEntity"/>
    </rdf:Description>
    """)
    add = current_template.substitute(uri=uri)
    sub = ""
    return [add, sub]

def update_contact(person_uri, contact_data):
    """
    Given the URI of a person and authoritative contact data, use five case
    logic to generate addition and subtration RDF as necessary to update the
    information in VIVO to reflect the authoritative information
    """
    properties = {'first_name':'foaf:firstName',
                  'last_name':'foaf:lastName',
                  'middle_name':'vivo:middleName',
                  'name_prefix':'bibo:prefixName',
                  'name_suffix':'bibo:suffixName',
                  'display_name':'rdfs:label',
                  'gatorlink':'ufVivo:gatorlink',
                  'preferred_title':'vivo:preferredTitle',
                  'primary_email':'vivo:primaryEmail',
                  'primary_phone_number':'vivo:primaryPhoneNumber',
                  'fax_number':'vivo:faxNumber'}
    ardf = ""
    srdf = ""
    person = vt.get_person(person_uri)

    for property in properties.keys():
        if property in person:
            vivo_value = person[property]
            if vivo_value == "":
                vivo_value = None
        else:
            vivo_value = None
        if property in contact_data:
            source_value = contact_data[property]
            if source_value == "":
                source_value = None
        else:
            source_value = None
        [add, sub] = vt.update_data_property(person_uri, properties[property],
                                         vivo_value, source_value)
        ardf = ardf + add
        srdf = srdf + sub

    # We update the home department for the person

    if 'home_deptid' in contact_data:
        if 'home_dept_uri' in person:
            vivo_value = person['home_dept_uri']
        else:
            vivo_value = None

        deptid = contact_data['home_deptid']
        try:
            contact_data['home_dept_uri'] = deptid_dictionary[deptid]
        except:
            raise DeptIDNotInVIVOException(deptid)
            return [adrf, srdf]

        if 'home_dept_uri' in contact_data:
            source_value = contact_data['home_dept_uri']
        else:
            source_value = None

        [add, sub] = vt.update_resource_property(person['person_uri'],
            'ufVivo:homeDept', vivo_value, source_value)
        ardf = ardf + add
        srdf = srdf + sub
    return [ardf, srdf]

# Driver program starts here

debug = True

sample = 1.0 # Fraction of records to be processed.  Set to 1.0 to process all

add_file = open("people_add.rdf", "w")
sub_file = open("people_sub.rdf", "w")
log_file = sys.stdout
exc_file = open("people_exc.txt", "w")

print >>log_file, datetime.now(), "Person Ingest Version", __version__
print >>log_file, datetime.now(), "VIVOTools Version", vt.__version__

print >>add_file, vt.rdf_header()
print >>sub_file, vt.rdf_header()

print >>log_file, datetime.now(), "Make URI Exception Dictionary"
uri_exception_dictionary =\
    make_uri_exception_dictionary(filename='uri_exceptions.csv',
                                  debug=debug)
print >>log_file, datetime.now(), "URI exception dictionary has ",\
    len(uri_exception_dictionary), " entries"

print >>log_file, datetime.now(), "Make UF DeptID Exception Dictionary"
deptid_exception_dictionary =\
    make_deptid_exception_dictionary(filename='deptid_exceptions.csv',
                                     debug=debug)
print >>log_file, datetime.now(), "UF DeptID exception dictionary has ",\
    len(deptid_exception_dictionary), " entries"

print >>log_file, datetime.now(), "Make UF UFID Exception List"
ufid_exception_dictionary =\
    make_ufid_exception_dictionary(filename='ufid_exceptions.csv',
                                   debug=debug)
print >>log_file, datetime.now(), "UF UFID exception dictionary has ",\
    len(ufid_exception_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO DeptID dictionary"
deptid_dictionary = vt.make_deptid_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO DeptID dictionary has ",\
    len(deptid_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO UFID Dictionary"
ufid_dictionary = vt.make_ufid_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO UFID dictionary has ",\
    len(ufid_dictionary), " entries"

print >>log_file, datetime.now(), "Make UF HR dictionary"
hr_dictionary = make_hr_dictionary(filename='position_data.csv', debug=debug)
print >>log_file, datetime.now(), "UF HR dictionary has ", len(hr_dictionary),\
    " entries"

#   Loop through the HR data and the VIVO data, adding each UFID to the
#   action report.  1 for HR only.  2 for VIVO only.  3 for both

print >>log_file, datetime.now(), "Create action report"
action_report = {} # determine the action to be taken for each UFID
for ufid in hr_dictionary.keys():
    action_report[ufid] = action_report.get(ufid, 0) + 1
for ufid in ufid_dictionary.keys():
    action_report[ufid] = action_report.get(ufid, 0) + 2
print >>log_file, datetime.now(), "Action report has ", len(action_report),\
    "entries"

print >>log_file, datetime.now(), "Make UF privacy dictionary"
privacy_dictionary = make_privacy_dictionary('privacy_data.csv', action_report,\
                                             debug=debug)
print >>log_file, datetime.now(), "UF Privacy dictionary has ",\
    len(privacy_dictionary), " entries"

print >>log_file, datetime.now(), "Make UF Contact dictionary"
contact_dictionary = make_contact_dictionary('contact_data.csv',
                                             action_report, debug=debug)
print >>log_file, datetime.now(), "UF Contact dictionary has ",\
    len(contact_dictionary), " entries"

print >>log_file, datetime.now(), "Count the three cases"

#   Loop through the action report for each UFID.  Count and log the cases

n1 = 0
n2 = 0
n3 = 0
i = 0
for ufid in action_report.keys():
    if action_report[ufid] == 1:
        n1 = n1 + 1
    elif action_report[ufid] == 2:
        n2 = n2 + 1
    else:
        n3 = n3 + 1

print >>log_file, datetime.now(), "Results:"
print >>log_file, n1,\
    " UFID in HR only.  These will be added to VIVO."
print >>log_file, n2,\
    " UFID in VIVO only.  Current and contact info will be removed"
print >>log_file, n3,\
    " UFID in both HR and VIVO.  Will be marked Current and position updated."

# Loop through the action report.  Process each ufid

n1add = 0
n1skip = 0
n1all = 0

print >>log_file, datetime.now(), "Begin Processing"
for ufid in sorted(action_report.keys()):

    ardf = ""
    srdf = ""
    r = random.random()
    if action_report[ufid] == 1:

        # Case 1: HR Only. Add Person to VIVO. Add Position.

        if r > sample:
            continue

        print >>log_file, "Case 1: Add   ", ufid,
        n1all = n1all + 1

        try:
            data = dict(hr_dictionary[ufid].items()+
                        contact_dictionary[ufid].items())
        except:
            n1skip = n1skip + 1
            print >>exc_file, "UFID  ", ufid, "No contact data"
            print >>log_file, "UFID  ", ufid, "No contact data"
            continue

        # Get URI for home department

        if 'home_deptid' in data and data['home_deptid'] != '':
            try:
                data['duri'] = deptid_dictionary[data['home_deptid']]
            except:
                n1skip = n1skip + 1
                print >>exc_file, "Home DeptID", data['home_deptid'], \
                    "Add Person can't find deptid"
                print >>log_file, "Home DeptID", data['home_deptid'], \
                    "Add Person can't find deptid"
                continue

        # Get URI for department of position

        if 'DEPTID' in data and data['DEPTID'] != '':
            try:
                data['org_uri'] = deptid_dictionary[data['DEPTID']]
            except:
                n1skip = n1skip + 1
                print >>exc_file, "Pos DeptID", data['DEPTID'], \
                    "Add Person can't find deptid"
                print >>log_file, "Pos DeptID", data['DEPTID'], \
                    "Add Person can't find deptid"
                continue

        #   Only add people that qualify
        #
        #   A person must either have a position_type or be a person who
        #   will not have a position entered, and regardless of position
        #   qualification, the other qualifications always apply

        if (not ok_position(data) or data['position_type'] is not None) and \
            ok_deptid(data['DEPTID']) and \
            ok_privacy(ufid) and \
            ok_ufid(ufid) and ok_position_title(data['position_label']):

            # Qualifies.  Go forward with Add

            print >>log_file, "Okay to add to VIVO", data,
            n1add = n1add + 1

            [add, puri] = add_person(data)
            data['person_uri'] = puri
            ardf = ardf + add

            # Qualify the position

            if ok_position(data) and ok_position_title(data['position_label']) \
               and ok_deptid(data['DEPTID']):
                [add, position_uri] = add_position(data)
                ardf = ardf + add
                print >>log_file, " Added to VIVO at ", puri
            else:
                print >>log_file, " No position added for", puri

        else:

            # Does not Qualify.  Write to log

            print >>log_file, "Does not Qualify"
            n1skip = n1skip + 1

    elif action_report[ufid] == 2:

        # Case 2: VIVO Only.  Process the person as former.

        if r > sample:
            continue

        person_uri = ufid_dictionary[ufid]

        # If the person is on the uri exception list, skip them

        if person_uri in uri_exception_dictionary:
            print >>log_file, "Case 2: NoEdit", ufid, person_uri
            continue

        print >>log_file, "Case 2: Former", ufid, ufid_dictionary[ufid]
        [add, sub] = former_person(person_uri)
        ardf = ardf + add
        srdf = srdf + sub

    else:

        # Case 3: HR and VIVO. Update Position. Update Current. Update Contact.

        if r > sample:
            continue

        person_uri = ufid_dictionary[ufid]

        # If the person is on the uri exception list, skip them

        if person_uri in uri_exception_dictionary:
            print >>log_file, "Case 3: NoEdit", ufid, person_uri
            continue

        print >>log_file, "Case 3: Update", ufid, person_uri

        # Mark as current

        [add, sub] = current_person(person_uri)
        ardf = ardf + add
        srdf = srdf + sub

        # Update contact

        try:
            contact_data = contact_dictionary[ufid]
        except:
            print >>exc_file, "UFID  ", ufid, "Case 3: No contact data for UFID"
            continue
        try:
            [add, sub] = update_contact(person_uri, contact_data)
            ardf = ardf + add
            srdf = srdf + sub
        except DeptIDNotInVIVOException as deptid:
            print >>exc_file, "DeptID", deptid,\
                "Case 3: Can't add home dept. DeptID not in VIVO"

        # Update position

        try:
            [add, sub] = update_position(person_uri, hr_dictionary[ufid])
            ardf = ardf + add
            srdf = srdf + sub
        except DeptIDNotInVIVOException as deptid:
            print >>exc_file, "DeptID", deptid,\
                "Case 3: Can't add position. DeptID not in VIVO"

    if ardf != "":
        print >>add_file, ardf
    if srdf != "":
        print >>sub_file, srdf

#   Done processing the UFIDs.  Wrap-up

print >>add_file, vt.rdf_footer()
print >>sub_file, vt.rdf_footer()

print >>log_file, "Case 1 All", n1all
print >>log_file, "Case 1 Added", n1add
print >>log_file, "Case 1 Skipped", n1skip
print >>log_file, datetime.now(), "End Processing"

add_file.close()
sub_file.close()
# log_file.close()
exc_file.close()
