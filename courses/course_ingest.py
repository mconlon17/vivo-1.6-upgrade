#!/usr/bin/env/python

"""
    course-ingest.py: Given course and section data from the Office of the
    University Registrar (from the Enterprise Data Warehouse), add courses
    as necessary, and course sections of courses.  Links courses to instructors
    vis teacher roles, create a course web site object for each course.  Link
    Sections (instances of courses) to course, instructor (via teacher role)
    and to academic term.  Academic terms are created by hand.

    Exceptions are thrown, caught and logged for missing academic term and
    missing instructor.

    Addition RDF is created.  No subtraction RDF is created.

    Version 0.0 MC 2013-08-03
    --  Read OUR data and UFID person data from VIVO. Create the process frame,
        throw and catch exceptions
    Version 0.1 MC 2013-10-03
    --  Remove redundant bi-directional assertions.  These will be added by
        the inferencer
    --  Write a position-data file for all people to be added
    --  Took out references to sub file
    --  Passed XML validator
    Version 0.2 MC 2013-10-10
    --  Correct ontology errors in roles, Course and Course section
    --  remove functions to make reverse assertions that will be handled by
        inferencer
    Version 0.3 MC 2013-10-19
    --  Added UFEntity to course and section to support distinguishing from
        courses and sections people may have taught outside UF
    --  Moved CourseRole creation to make_section.  All linkages between
        entities are added at the section level.
    --  Show vivotools version
    Version 0.4 MC 2013-12-15
    --  escape the course title to prevent RDF ingest errors
    Version 0.5 MC 2014-06-23
    --  Handle unicode using standard vivotools approach.
    --  Use codecs to write XML.
    --  Add labels to the TeacherRole for courses -- this is a
        workaround required by the VIVO interface.
    --  Fix bug regarding TeacherRoles for courses -- these must be
        singular, not one per section.
    --  Fix version number in RDF
    --  Improve code formatting
    --  Clean up print destinations
    --  Runs with current vivotools

    Future enhancements:
     -- Handle instructor new to existing section (team teaching).

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2013, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.5"

from datetime import datetime
import os
import sys
import pickle
import random # for testing purposes, select subsets of records to process
import tempita
import vivotools as vt
import codecs

action_report = {} # determine the action to be taken for each UFID

class NoSuchAcademicTermException(Exception):
    """
    Academic terms in the OUR data are compared to VIVO.  If the academic term
    is not found in VIVO, this exception is thrown.
    """
    pass

class NoSuchPersonException(Exception):
    """
    Every UFID from the OUR is checked against VIVO.  If the instructor can not
    be found, this exception is thrown.
    """
    pass

def make_course_rdf(taught_data):
    """
    Given taught_data, generate the RDF for a course,
    a teacher role and links between course, teacher role and instructor
    """
    course_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{course_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/Course"/>
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFEntity"/>
        <rdfs:label>{{course_name}}</rdfs:label>
        <ufVivo:courseNum>{{course_number}}</ufVivo:courseNum>
        <ufVivo:harvestedBy>Python Courses version 0.5</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>""")
    course_uri = vt.get_vivo_uri()
    rdf = course_rdf_template.substitute(course_uri=course_uri,
        course_name=taught_data['course_name'],
        course_number=taught_data['course_number'],
        harvest_datetime=vt.make_harvest_datetime(),
        person_uri=taught_data['person_uri'])
    return [rdf, course_uri]

def make_section_rdf(taught_data):
    """
    Given teaching data, make a section and a teaching role.  Link
    the section to its teaching role, to its course and term.  Link the
    role to the instructor.
    """
    section_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{section_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/CourseSection"/>
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFEntity"/>
        <rdfs:label>{{section_name}}</rdfs:label>
        <ufVivo:sectionNum>{{section_number}}</ufVivo:sectionNum>
        <vivo:dateTimeInterval rdf:resource="{{term_uri}}"/>
        <ufVivo:sectionForCourse rdf:resource="{{course_uri}}"/>
        <ufVivo:harvestedBy>Python Courses version 0.5</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    <rdf:Description rdf:about="{{term_uri}}">
        <ufVivo:dateTimeIntervalFor rdf:resource="{{section_uri}}"/>
    </rdf:Description>
    {{if course_new}}
        <rdf:Description rdf:about="{{course_role_uri}}">
            <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
            <rdf:type rdf:resource="http://vivoweb.org/ontology/core#TeacherRole"/>
            <rdfs:label>{{course_name}}</rdfs:label>
            <ufVivo:courseRoleOf rdf:resource="{{person_uri}}"/>
            <vivo:roleRealizedIn rdf:resource="{{course_uri}}"/>        
        </rdf:Description>
    {{endif}}
    <rdf:Description rdf:about="{{teacher_role_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#TeacherRole"/>
        <vivo:teacherRoleOf rdf:resource="{{person_uri}}"/>
        <vivo:roleRealizedIn rdf:resource="{{section_uri}}"/>
    </rdf:Description>""")

    section_uri = vt.get_vivo_uri()
    rdf = section_rdf_template.substitute(section_uri=section_uri,
        section_name=taught_data['section_name'],
        section_number=taught_data['section_number'],
        term_uri=taught_data['term_uri'],
        course_uri=taught_data['course_uri'],
        course_name=taught_data['course_name'],
        course_new=taught_data['course_new'],
        teacher_role_uri=vt.get_vivo_uri(),
        course_role_uri=vt.get_vivo_uri(),     
        person_uri=taught_data['person_uri'],
        harvest_datetime=vt.make_harvest_datetime())
    return [rdf, section_uri]

def make_taught_dictionary(filename="course_data.csv", debug=False):
    """
    Read a CSV file with course data.  Create a dictionary with one entry
    per OUR record
    """
    if os.path.isfile('taught_data.pcl'):
        taught_dictionary = pickle.load(open('taught_data.pcl', 'r'))
        return taught_dictionary
    taught_dictionary = vt.read_csv(filename)

    for row in taught_dictionary.keys():
        taught_data = taught_dictionary[row]
        taught_data['ufid'] = taught_data['UF_UFID'].ljust(8, '0')
        taught_data['term_name'] = term_name(taught_data['UF_TERM'])
        taught_data['course_number'] = taught_data['UF_COURSE_CD']
        taught_data['course_name'] = taught_data['course_number'] +\
            ' ' + taught_data['UF_COURSE_NAME'].title()
        taught_data['section_number'] = taught_data['UF_SECTION']
        taught_data['section_name'] = taught_data['course_number'] + ' ' + \
                                      taught_data['term_name'] + ' ' + \
                                      taught_data['UF_SECTION']
        taught_dictionary[row] = taught_data

    if debug:
        print >>log_file, datetime.now(), "Taught Data has",\
            len(taught_dictionary), "rows"
        print >>log_file, datetime.now(), "First row",\
            taught_dictionary[1]

    pickle.dump(taught_dictionary, open('taught_data.pcl', 'w'))
    return taught_dictionary

def term_name(term_number):
    """
    Given a UF term number, return the UF term name
    """
    year = term_number[0:4]
    term = term_number[4:5]
    if term == "1":
        term_name = "Spring "+str(year)
    elif term == "5" or term == "6" or term == "7":
        term_name = "Summer "+str(year)
    elif term == "8":
        term_name = "Fall "+str(year)
    else:
        print term_number, year, term
        raise NoSuchAcademicTermException(term_number)
    return term_name

def make_term_dictionary(debug=False):
    """
    Make a term dictionary for academic terms.  Key is term name such as
    "Spring 2011".  Value is URI.
    """
    query = tempita.Template("""
    SELECT ?x ?label
    WHERE {
      ?x a vivo:AcademicTerm .
      ?x rdfs:label ?label .
    }""")
    query = query.substitute()
    result = vt.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0],\
            result["results"]["bindings"][1]

    term_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        term = b['label']['value']
        uri = b['x']['value']
        term_dictionary[term] = uri
        i = i + 1

    return term_dictionary

def make_course_dictionary(debug=False):
    """
    Make a course dictionary from VIVO contents.  Key is course number
    such as ABF2010C. Value is URI.
    """
    query = tempita.Template("""
    SELECT ?x ?label ?coursenum
    WHERE {
      ?x a ufVivo:Course .
      ?x ufVivo:courseNum ?coursenum .
    }""")
    query = query.substitute()
    result = vt.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0],\
            result["results"]["bindings"][1]

    course_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        coursenum = b['coursenum']['value']
        uri = b['x']['value']
        course_dictionary[coursenum] = uri
        i = i + 1

    return course_dictionary

def make_section_dictionary(debug=False):
    """
    Make a section dictionary from VIVO contents.  Key is section number.
    Value is URI.
    """
    query = tempita.Template("""
    SELECT ?x ?label
        WHERE {
        ?x a ufVivo:CourseSection .
        ?x rdfs:label ?label .
    }""")
    query = query.substitute()
    result = vt.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0],\
            result["results"]["bindings"][1]

    section_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        label = b['label']['value']
        uri = b['x']['value']
        section_dictionary[label] = uri
        i = i + 1

        if debug and i % 1000 == 0:
            print i, label, uri

    return section_dictionary

# Driver program starts here

debug = False
sample = 1.0 # Fraction of records to be processed.  Set to 1.0 to process all

file_name = "courses"
add_file = codecs.open(file_name+"_add.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
pos_file = codecs.open(file_name+"_pos.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
log_file = codecs.open(file_name+"_log.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
exc_file = codecs.open(file_name+"_exc.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')

add_ufid = {}

print >>add_file, vt.rdf_header()

print >>log_file, datetime.now(), "Course ingest. Version", __version__,\
    "VIVOTools", vt.__version__
print >>log_file, datetime.now(), "Make UF Taught Dictionary"
taught_dictionary = make_taught_dictionary(filename='course_data.csv',\
    debug=debug)
print >>log_file, datetime.now(), "Taught dictionary has ",\
    len(taught_dictionary), " entries"
print >>log_file, datetime.now(), "Make VIVO Term Dictionary"
term_dictionary = make_term_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO Term dictionary has ",\
    len(term_dictionary), " entries"
print >>log_file, datetime.now(), "Make VIVO Course Dictionary"
course_dictionary = make_course_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO Course dictionary has ",\
    len(course_dictionary), " entries"
print >>log_file, datetime.now(), "Make VIVO Section Dictionary"
section_dictionary = make_section_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO Section dictionary has ",\
    len(section_dictionary), " entries"
print >>log_file, datetime.now(), "Make VIVO UFID Dictionary"
ufid_dictionary = vt.make_ufid_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO UFID dictionary has ",\
    len(ufid_dictionary), " entries"

# Loop through the course data.  Process each row

print >>log_file, datetime.now(), "Begin Processing"
for row in taught_dictionary.keys():

    r = random.random()
    if r > sample:
        continue

    ardf = ""
    taught_data = taught_dictionary[row]

    # Look for the instructor.  If not found, write to exception log

    try:
        person_uri = ufid_dictionary[taught_data['ufid']]
        taught_data['person_uri'] = person_uri
    except:
        print >>exc_file, "No such instructor on row", row, "UFID = ", \
            taught_data['ufid']
        add_ufid[taught_data['ufid']] = True

        continue

    # Look for the term.  If not found, write to exception log

    try:
        term_uri = term_dictionary[taught_data['term_name']]
        taught_data['term_uri'] = term_uri
    except:
        print >>exc_file, "No such term on row", row, "Term = ",\
            taught_data['term_name']
        continue

    # Look for the course.  If not found, add it

    try:
        course_uri = course_dictionary[taught_data['course_number']]
        taught_data['course_new'] = False
    except:
        [add, course_uri] = make_course_rdf(taught_data)
        ardf = ardf + add
        print >>log_file, "Add course", taught_data['course_name'],\
            "at", course_uri
        course_dictionary[taught_data['course_number']] = course_uri
        taught_data['course_new'] = True
    taught_data['course_uri'] = course_uri

    # Look for the section.  If not found, add it

    try:
        section_uri = section_dictionary[taught_data['section_name']]
    except:
        [add, section_uri] = make_section_rdf(taught_data)
        print >>log_file, "Add section", taught_data['section_name'],\
            "at", section_uri
        ardf = ardf + add
        section_dictionary[taught_data['section_name']] = section_uri

    taught_data['section_uri'] = section_uri

    if ardf != "":
        add_file.write(ardf)

#   Done processing the courses.  Wrap-up

for ufid in sorted(add_ufid.keys()):

    # Write records into a position file.  Records have the UFID to be
    # added to VIVO, along with a zero in the HR_POSITION field (last
    # field) indicating to person_ingest that no position should be created
    # for the UFID being added.

    print >>pos_file, "NULL" + "|" + ufid + "|" + \
        "NULL" + "|" + "NULL" + "|" + "NULL" + "|" + "NULL" + "|" + \
        "NULL" + "|" + "0"

print >>add_file, vt.rdf_footer()
print >>log_file, datetime.now(), "End Processing"

add_file.close()
log_file.close()
exc_file.close()
pos_file.close()
