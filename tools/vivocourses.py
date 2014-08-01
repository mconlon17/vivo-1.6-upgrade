#!/usr/bin/env/python

"""
    vivocourses.py -- tools for courses and course section in VIVO

    See CHANGELOG.md for history

    To Do:
    --  write test functions
    --  get rid of tempita
    --  update for VIVO-ISF
    --  replace make_x_rdf series with add_x series
    --  get rid of count and i in dictionary functions.  Iterate over results
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.0"

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
