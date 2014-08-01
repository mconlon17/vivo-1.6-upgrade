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

    See CHANGELOG.md for history

    To Do:
    --  Use a prepare function to go through the data
    --  Use tools from vivocourses
    --  Move to an update designl. Even though updates are rare, we need to
        be able to handle them
    --  Update for VIVO-ISF
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.6"

from datetime import datetime
import os
import sys
import codecs

action_report = {} # determine the action to be taken for each UFID

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
