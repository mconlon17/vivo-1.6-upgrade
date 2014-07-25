#!/usr/bin/env/python
""" vivopeople.py -- A library of useful things for working with people in VIVO

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "2.00"

import re

def repair_email(email, exp = re.compile(r'\w+\.*\w+@\w+\.(\w+\.*)*\w+')):
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

def repair_phone_number(phone, debug=False):
    """
    Given an arbitrary string that attempts to represent a phone number,
    return a best attempt to format the phone number according to ITU standards

    If the phone number can not be repaired, the function reurns an empty string
    """
    phone_text = phone.encode('ascii', 'ignore') # encode to ascii
    phone_text = phone_text.lower()
    phone_text = phone_text.strip()
    extension_digits = None
    #
    # strip off US international country code
    #
    if phone_text.find('+1 ') == 0:
        phone_text = phone_text[3:]
    if phone_text.find('+1-') == 0:
        phone_text = phone_text[3:]
    if phone_text.find('(1)') == 0:
        phone_text = phone_text[3:]
    digits = []
    for c in list(phone_text):
        if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            digits.append(c)
    if len(digits) > 10:
        # pull off the extension
        i = phone_text.rfind(' ') # last blank
        if i > 0:
            extension = phone_text[i+1:]
            extension_digits = []
            for c in list(extension):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    extension_digits.append(c)
            digits = [] # recalc the digits
            for c in list(phone_text[:i+1]):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    digits.append(c)
        elif phone_text.rfind('x') > 0:
            i = phone_text.rfind('x')
            extension = phone_text[i+1:]
            extension_digits = []
            for c in list(extension):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    extension_digits.append(c)
            digits = [] # recalc the digits
            for c in list(phone_text[:i+1]):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    digits.append(c)
        else:
            extension_digits = digits[10:]
            digits = digits[:10]
    if len(digits) == 7:
        if phone[0:5] == '352392':
            updated_phone = '' # Damaged UF phone number, nothing to repair
            extension_digits = None
        elif phone[0:5] == '352273':
            updated_phone = '' # Another damaged phone number, not to repair
            extension_digits = None
        else:
            updated_phone = '(352) ' + "".join(digits[0:3])+'-'+ \
                "".join(digits[3:7])
    elif len(digits) == 10:
        updated_phone = '('+"".join(digits[0:3])+') '+"".join(digits[3:6])+ \
            '-'+"".join(digits[6:10])
    elif len(digits) == 5 and digits[0] == '2': # UF special
        updated_phone = '(352) 392' + "".join(digits[1:5])
    elif len(digits) == 5 and digits[0] == '3': # another UF special
        updated_phone = '(352) 273' + "".join(digits[1:5])
    else:
        updated_phone = '' # no repair
        extension_digits = None
    if extension_digits is not None and len(extension_digits) > 0:
        updated_phone = updated_phone + ' ext. ' + "".join(extension_digits)
    if debug:
        print phone.ljust(25), updated_phone.ljust(25)
    return updated_phone

def get_position_type(salary_plan):
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

def improve_jobcode_description(s):
    """
    HR uses a series of abbreviations to fit job titles into limited text
    strings.
    Here we attempt to reverse the process -- a short title is turned into a
    longer one
    """

    s = s.lower() # convert to lower
    s = s.title() # uppercase each word
    s = s + ' '   # add a trailing space so we can find these abbreviated
                  # words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @") # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace("-", " #")
    t = t.replace("Aca ", "Academic ")
    t = t.replace("Act ", "Acting ")
    t = t.replace("Advanc ", "Advanced ")
    t = t.replace("Adv ", "Advisory ")
    t = t.replace("Agric ", "Agricultural ")
    t = t.replace("Alumn Aff ", "Alumni Affairs ")
    t = t.replace("Ast #R ", "Research Assistant ")
    t = t.replace("Ast #G ", "Grading Assistant ")
    t = t.replace("Ast #T ", "Teaching Assistant ")
    t = t.replace("Ast ", "Assistant ")
    t = t.replace("Affl ", "Affiliate ")
    t = t.replace("Aso ", "Associate ")
    t = t.replace("Asoc ", "Associate ")
    t = t.replace("Assoc ", "Associate ")
    t = t.replace("Bio ", "Biological ")
    t = t.replace("Prof ", "Professor ")
    t = t.replace("Mstr ", "Master ")
    t = t.replace("Couns ", "Counselor ")
    t = t.replace("Adj ", "Adjunct ")
    t = t.replace("Dist ", "Distinguished ")
    t = t.replace("Chr ", "Chair ")
    t = t.replace("Cio ", "Chief Information Officer ")
    t = t.replace("Coo ", "Chief Operating Officer ")
    t = t.replace("Coord ", "Coordinator ")
    t = t.replace("Co ", "Courtesy ")
    t = t.replace("Clin ", "Clinical ")
    t = t.replace("Dn ", "Dean ")
    t = t.replace("Finan ", "Financial ")
    t = t.replace("Stu ", "Student ")
    t = t.replace("Prg ", "Program ")
    t = t.replace("Dev ", "Development ")
    t = t.replace("Aff ", "Affiliate ")
    t = t.replace("Svcs ", "Services ")
    t = t.replace("Devel ", "Development ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Progs ", "Programs ")
    t = t.replace("Facil ", "Facility ")
    t = t.replace("Hlth ", "Health ")
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
    t = t.replace("Rsrh ", "Research ")
    t = t.replace("Ret ", "Retirement ")
    t = t.replace("Sch ", "School ")
    t = t.replace("Sci ", "Scientist ")
    t = t.replace("Svcs ", "Services ")
    t = t.replace("Serv ", "Service ")
    t = t.replace("Tch ", "Teaching ")
    t = t.replace("Tele ", "Telecommunications ")
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
    t = t.replace("Spc ", "Specialist ")
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
    t = t.replace("Vp ", "Vice President ")
    t = t.replace(" @", "/") # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" #", "-") # restore -
    return t[:-1] # Take off the trailing space

def get_position_uris(person_uri):
    """
    Given a person_uri, return a list of the position_uris for that
    person.  If none, return an empty list
    """
    from vivofoundation import vivo_sparql_query
    position_uris = []
    query = """
    #  Return the uri of positions for a person

    SELECT ?position_uri
      WHERE {
        <person_uri> vivo:relatedBy ?position_uri .
        ?position_uri rdf:type vivo:Position .
    }
    group by ?position_uri
    """
    query = query.replace('person_uri', person_uri)
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        position_uris.append(b['position_uri']['value'])
        i = i + 1
    return position_uris

def get_telephone(telephone_uri):
    """
    Given the uri of a telephone number, return the uri, number and type
    """
    from vivofoundation import get_triples
    telephone = {'telephone_uri':telephone_uri}
    type = ""
    triples = get_triples(telephone_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://www.w3.org/2006/vcard/ns#telephone":
            telephone['telephone_number'] = o
        if p == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            if o.startswith('http://www.w3.org/2006/vcard'):
                ptype = o[32:]
                if type == "" or type == "Telephone" and ptype == "Fax" \
                    or ptype == "Telephone":
                    type = ptype
        i = i + 1
    telephone['telephone_type'] = type
    return telephone

def get_name(name_uri):
    """
    Given the uri of a vcard name entity, get all the data values
    associated with the entity
    """
    from vivofoundation import get_triples
    name = {'name_uri':name_uri}
    triples = get_triples(name_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://www.w3.org/2006/vcard/ns#givenName":
            name['given_name'] = o
        if p == "http://www.w3.org/2006/vcard/ns#familyName":
            name['family_name'] = o
        if p == "http://www.w3.org/2006/vcard/ns#additionalName":
            name['additional_name'] = o
        if p == "http://www.w3.org/2006/vcard/ns#honorificPrefix":
            name['name_prefix'] = o
        if p == "http://www.w3.org/2006/vcard/ns#honorificSuffix":
            name['name_suffix'] = o
        i = i + 1
    return name

def get_vcard(vcard_uri):
    """
    Given the uri of a vcard, get all the data values and uris associated with
    the vcard
    """
    from vivofoundation import get_triples
    from vivofoundation import get_vivo_value
    vcard = {'vcard_uri':vcard_uri}
    vcard['telephone_uris'] = []
    vcard['email_uris'] = []
    triples = get_triples(vcard_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://www.w3.org/2006/vcard/ns#hasTitle":
            vcard['title_uri'] = o
        if p == "http://purl.obolibrary.org/obo/ARG_2000029":
            vcard['person_uri'] = o
        if p == "http://www.w3.org/2006/vcard/ns#hasTelephone":
            vcard['telephone_uris'].append(o)
        if p == "http://www.w3.org/2006/vcard/ns#hasName":
            vcard['name_uri'] = o
        if p == "http://www.w3.org/2006/vcard/ns#hasEmail":
            vcard['email_uris'].append(o)
        i = i + 1

    # And now deref each of the uris to get the data values.

    vcard['name'] = get_name(vcard['name_uri'])

    if vcard.get('title_uri', None) is not None:
        vcard['title'] = get_vivo_value(vcard['title_uri'],'vcard:title')

    vcard['telephones'] = []
    for telephone_uri in vcard['telephone_uris']:
        vcard['telephones'].append(get_telephone(telephone_uri))
    del vcard['telephone_uris']

    vcard['email_addresses'] = []
    for email_uri in vcard['email_uris']:
        vcard['email_addresses'].append({
            'email_uri':email_uri,
            'email_address':get_vivo_value(email_uri,
                                              "vcard:email")
            })
    del vcard['email_uris']
    return vcard

def get_person(person_uri, get_contact=True):
    """
    Given the URI of a person in VIVO, get the poerson's attributes and
    return a flat, keyed structure appropriate for update and other
    applications.

    To Do:
    Add get_grants, get_papers, etc as we had previously
    """
    from vivofoundation import get_triples
    person = {'person_uri': person_uri}
    triples = get_triples(person_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == \
           "http://vitro.mannlib.cornell.edu/ns/vitro/0.7#mostSpecificType":
            person['person_type'] = o
        if p == "http://purl.obolibrary.org/obo/ARG_2000028":
            person['vcard_uri'] = o
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            person['display_name'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/ufid":
            person['ufid'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/homeDept":
            person['homedept_uri'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/privacyFlag":
            person['privacy_flag'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/gatorlink":
            person['gatorlink'] = o
        if p == "http://vivoweb.org/ontology/core#eRACommonsId":
            person['eracommonsid'] = o
        i = i + 1

    # deref the vcard

    if get_contact == True:
        person['vcard'] = get_vcard(person['vcard_uri'])
        
    return person

def get_degree(degree_uri):
    """
    Given a URI, return an object that contains the degree (educational
    training) it represents

    """
    degree = {'degree_uri':degree_uri}
    triples = get_triples(degree_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#majorField":
            degree['major_field'] = o

        # deref the academic degree

        if p == "http://vivoweb.org/ontology/core#degreeEarned":
            degree['earned_uri'] = o
            degree['degree_name'] = get_vivo_value(o, 'core:abbreviation')

        # deref the Institution

        if p == "http://vivoweb.org/ontology/core#trainingAtOrganization":
            degree['training_institution_uri'] = o
            institution = get_organization(o)
            if 'label' in institution: # home department might be incomplete
                degree['institution_name'] = institution['label']

        # deref the datetime interval

        if p == "http://vivoweb.org/ontology/core#dateTimeInterval":
            datetime_interval = get_datetime_interval(o)
            degree['datetime_interval'] = datetime_interval
            if 'start_date' in datetime_interval:
                degree['start_date'] = datetime_interval['start_date']
            if 'end_date' in datetime_interval:
                degree['end_date'] = datetime_interval['end_date']
        i = i + 1
    return degree

def get_role(role_uri):
    """
    Given a URI, return an object that contains the role it represents

    To Do:
    Generalize to more types of roles
    """
    role = {'role_uri':role_uri}
    triples = get_triples(role_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#roleIn":
            role['grant_uri'] = o
        if p == "http://vivoweb.org/ontology/core#roleContributesTo":
            role['grant_uri'] = o
        if p == 'http://vivoweb.org/ontology/core#' \
            'co-PrincipalInvestigatorRoleOf':
            role['co_principal_investigator_role_of'] = o
        if p == 'http://vivoweb.org/ontology/core#' \
            'principalInvestigatorRoleOf':
            role['principal_investigator_role_of'] = o
        if p == 'http://vivoweb.org/ontology/core#' \
            'investigatorRoleOf':
            role['investigator_role_of'] = o
        i = i + 1
    return role


def get_authorship(authorship_uri):
    """
    Given a URI, return an object that contains the authorship it represents
    """
    authorship = {'authorship_uri':authorship_uri}
    triples = get_triples(authorship_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#authorRank":
            authorship['author_rank'] = o
        if p == "http://vivoweb.org/ontology/core#linkedAuthor":
            authorship['author_uri'] = o
        if p == "http://vivoweb.org/ontology/core#linkedInformationResource":
            authorship['publication_uri'] = o
        if p == "http://vivoweb.org/ontology/core#isCorrespondingAuthor":
            authorship['corresponding_author'] = o
        i = i + 1
    return authorship

def get_webpage(webpage_uri):
    """
    Given a URI, return an object that contains the webpage it represents
    """
    webpage = {'webpage_uri':webpage_uri}
    triples = get_triples(webpage_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#webpageOf":
            webpage['webpage_of'] = o
        if p == "http://vivoweb.org/ontology/core#rank":
            webpage['rank'] = o
        if p == "http://vivoweb.org/ontology/core#linkURI":
            webpage['link_uri'] = o
        if p == "http://vivoweb.org/ontology/core#rank":
            webpage['rank'] = o
        if p == "http://vivoweb.org/ontology/core#linkAnchorText":
            webpage['link_anchor_text'] = o
        if o == "http://vivoweb.org/ontology/ufVivo#FullTextURI":
            webpage['link_type'] = "full_text"
        i = i + 1
    return webpage

def get_position(position_uri):
    """
    Given a URI, return an object that contains the position it represents
    """
    from vivofoundation import get_triples
    from vivofoundation import get_types
    from vivofoundation import get_datetime_interval
    from vivofoundation import untag_predicate
    
    position = {'position_uri':position_uri} # include position_uri
    triples = get_triples(position_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#relates":

            #   deref relates.  Get the types of the referent.  If its an org,
            #   assign the uri of the relates (o) to the org_uri of the
            #   position.  Otherwise, assume its the person_uri

            types = get_types(o)
            if untag_predicate('foaf:Organization') in types:
                position['position_orguri'] = o
            else:
                position['person_uri'] = o

        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/hrJobTitle":
            position['hr_title'] = o
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            position['position_label'] = o
        if o == "http://vivoweb.org/ontology/core#FacultyPosition":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/core#Non-FacultyAcademicPosition":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/vivo-ufl/ClinicalFacultyPosition":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/vivo-ufl/PostDocPosition":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/core#LibrarianPosition":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/core#Non-AcademicPosition":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/vivo-ufl/StudentAssistant":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/vivo-ufl/GraduateAssistant":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/vivo-ufl/Housestaff":
            position['position_type'] = o
        if o == "http://vivoweb.org/ontology/vivo-ufl/TemporaryFaculty":
            position['position_type'] = o
        if o == \
            "http://vivoweb.org/ontology/core#FacultyAdministrativePosition":
            position['position_type'] = o
        if p == "http://vivoweb.org/ontology/core#dateTimeInterval":
            datetime_interval = get_datetime_interval(o)
            position['datetime_interval'] = datetime_interval
            if 'start_date' in datetime_interval:
                position['start_date'] = datetime_interval['start_date']
            if 'end_date' in datetime_interval:
                position['end_date'] = datetime_interval['end_date']  
        i = i + 1

    return position

def get_publication(publication_uri, get_authors=True):
    """
    Given a URI, return an object that contains the publication it represents.
    We have to dereference the publication venue to get the journal name, and
    the datetime value to get the date of publication.

    The resulting object can be displayed using string_from_document
    """
    publication = {'publication_uri':publication_uri} #include the uri
    triples = get_triples(publication_uri)
    publication['grants_cited'] = []
    publication['keyword_list'] = []
    publication['concept_uris'] = []
    publication['authorship_uris'] = []
    publication['author_uris'] = []
    publication['authors'] = []
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']

        if p == "http://purl.org/ontology/bibo/doi":
            publication['doi'] = o
        if p == "http://purl.org/ontology/bibo/pmid":
            publication['pmid'] = o
        if p == "http://purl.org/ontology/bibo/abstract":
            publication['abstract'] = o
        if p == "http://vivoweb.org/ontology/core#pmcid":
            publication['pmcid'] = o
        if p == "http://vivoweb.org/ontology/core#nihmsid":
            publication['nihmsid'] = o
        if o == "http://purl.org/ontology/bibo/AcademicArticle":
            publication['publication_type'] = 'academic-article'
        if o == "http://purl.org/ontology/bibo/Book":
            publication['publication_type'] = 'book'
        if o == "http://purl.org/ontology/bibo/Chapter":
            publication['publication_type'] = 'chapter'
        if o == "http://vivoweb.org/ontology/core#ConferencePaper":
            publication['publication_type'] = 'conference-paper'
        if o == "http://vivoweb.org/ontology/core#ConferencePoster":
            publication['publication_type'] = 'conference-poster'
        if p == "http://vivoweb.org/ontology/core#freeTextKeyword":
            publication['keyword_list'].append(o)
        if p == "http://vivoweb.org/ontology/ufVivo#grantCited":
            publication['grants_cited'].append(o)
        if p == "http://vivoweb.org/ontology/core#hasSubjectArea":
            publication['concept_uris'].append(o)
        if p == \
            "http://vivoweb.org/ontology/core#informationResourceInAuthorship":
            publication['authorship_uris'].append(o)
        if p == "http://vivoweb.org/ontology/core#webPage":
            publication['web_page'] = o
        if p == "http://purl.org/ontology/bibo/pageStart":
            publication['page_start'] = o
        if p == "http://purl.org/ontology/bibo/pageEnd":
            publication['page_end'] = o
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            publication['title'] = o
        if p == "http://purl.org/ontology/bibo/volume":
            publication['volume'] = o
        if p == "http://purl.org/ontology/bibo/number":
            publication['number'] = o

        # deref the web page (does not handle multiple web pages)

        if p == "http://vivoweb.org/ontology/core#webPage":
            publication['web_page'] = get_webpage(o)
            if 'link_type' in web_page and web_page['link_type'] == \
               'full_text_uri':
                publication['full_text_uri'] = web_page['link_uri']

        # deref the publication_venue

        if p == "http://vivoweb.org/ontology/core#hasPublicationVenue":
            publication_venue = get_publication_venue(o)
            try:
                publication['journal'] = publication_venue['label']
            except:
                pass

        # deref the datetime

        if p == "http://vivoweb.org/ontology/core#dateTimeValue":
            datetime_value = get_datetime_value(o)
            try:
                publication['date'] = datetime_value['date']
            except:
                pass
        i = i + 1

    # deref the authorships

    if get_authors:
        authors = {}
        for authorship_uri in publication['authorship_uris']:
            authorship = get_authorship(authorship_uri)
            if 'author_uri' in authorship:

                #   Add key value which is rank.  Then string_from_document
                #   should show in rank order.  Voila!
                
                author_uri = authorship['author_uri']
                if 'author_rank' in authorship:
                    rank = authorship['author_rank']
                    authors[rank] = {'first':get_vivo_value(author_uri,
                        "foaf:firstName"), 'middle':get_vivo_value(author_uri,
                        "vivo:middleName"), 'last':get_vivo_value(author_uri,
                        "foaf:lastName")}
                publication['author_uris'].append(author_uri)
        publication['authors'] = authors

    return publication

def get_datetime_value(datetime_value_uri):
    """
    Given a URI, return an object that contains the datetime value it
    represents
    """
    datetime_value = {'datetime_value_uri':datetime_value_uri}
    triples = get_triples(datetime_value_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#dateTime":
            datetime_value['datetime'] = o
            year = o[0:4]
            month = o[5:7]
            day = o[8:10]
        if p == "http://vivoweb.org/ontology/core#dateTimePrecision":
            datetime_value['datetime_precision'] = o
            if datetime_value['datetime_precision'] == \
                "http://vivoweb.org/ontology/core#yearPrecision":
                datetime_value['datetime_precision'] = 'year'
            if datetime_value['datetime_precision'] == \
                "http://vivoweb.org/ontology/core#yearMonthPrecision":
                datetime_value['datetime_precision'] = 'year_month'
            if datetime_value['datetime_precision'] == \
                "http://vivoweb.org/ontology/core#yearMonthDayPrecision":
                datetime_value['datetime_precision'] = 'year_month_day'
        if 'datetime' in datetime_value and 'datetime_precision' in \
            datetime_value:
            if datetime_value['datetime_precision'] == "year":
                datetime_value['date'] = {'year':year}
            if datetime_value['datetime_precision'] == "year_month":
                datetime_value['date'] = {'year':year, 'month':month}
            if datetime_value['datetime_precision'] == "year_month_day":
                datetime_value['date'] = {'year':year, 'month':month, 'day':day}
        i = i + 1
    return datetime_value

def get_datetime_interval(datetime_interval_uri):
    """
    Given a URI, return an object that contains the datetime_interval it
    represents
    """
    datetime_interval = {'datetime_interval_uri':datetime_interval_uri}
    triples = get_triples(datetime_interval_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#start":
            datetime_value = get_datetime_value(o)
            datetime_interval['start_date'] = datetime_value
        if p == "http://vivoweb.org/ontology/core#end":
            datetime_value = get_datetime_value(o)
            datetime_interval['end_date'] = datetime_value
        i = i + 1
    return datetime_interval


def get_publication_venue(publication_venue_uri):
    """
    Given a URI, return an object that contains the publication venue it
    represents
    """
    publication_venue = {'publication_venue_uri':publication_venue_uri}
    triples = get_triples(publication_venue_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://purl.org/ontology/bibo/issn":
            publication_venue['issn'] = o
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            publication_venue['label'] = o
        i = i + 1
    return publication_venue

def get_grant(grant_uri, get_investigators=False):
    """
    Given a URI, return an object that contains the grant it represents
    """
    grant = {'grant_uri':grant_uri}
    grant['contributing_role_uris'] = []
    grant['pi_uris'] = []
    grant['coi_uris'] = []
    grant['inv_uris'] = []
    grant['role_uris'] = {}
    grant['investigators'] = []
    triples = get_triples(grant_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            grant['title'] = o
        if p == "http://vivoweb.org/ontology/core#totalAwardAmount":
            grant['total_award_amount'] = o
        if p == "http://vivoweb.org/ontology/core#grantDirectCosts":
            grant['grant_direct_costs'] = o
        if p == "http://purl.org/ontology/bibo/abstract":
            grant['abstract'] = o
        if p == "http://vivoweb.org/ontology/core#sponsorAwardId":
            grant['sponsor_award_id'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/dsrNumber":
            grant['dsr_number'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/psContractNumber":
            grant['pcn'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/dateHarvested":
            grant['date_harvested'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/harvestedBy":
            grant['harvested_by'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/localAwardId":
            grant['local_award_id'] = o
        if p == "http://vivoweb.org/ontology/core#contributingRole":
            grant['contributing_role_uris'].append(o['value'])
        
        # deref administered by

        if p == "http://vivoweb.org/ontology/core#administeredBy":
            grant['administered_by_uri'] = o['value']
            administered_by = get_organization(o['value'])
            if 'label' in administered_by:
                grant['administered_by'] = administered_by['label']

        # deref awarded by

        if p == "http://vivoweb.org/ontology/core#grantAwardedBy":
            grant['sponsor_uri'] = o['value']
            awarded_by = get_organization(o['value'])
            if 'label' in awarded_by:
                grant['awarded_by'] = awarded_by['label']

        # deref the datetime interval

        if p == "http://vivoweb.org/ontology/core#dateTimeInterval":
            grant['dti_uri'] = o['value']
            datetime_interval = get_datetime_interval(o['value'])
            grant['datetime_interval'] = datetime_interval
            if 'start_date' in datetime_interval:
                grant['start_date'] = datetime_interval['start_date']
            if 'end_date' in datetime_interval:
                grant['end_date'] = datetime_interval['end_date']

        i = i + 1

    # deref the roles

    for role_uri in grant['contributing_role_uris']:
        role = get_role(role_uri)
        if 'principal_investigator_role_of' in role:
            pi_uri = role['principal_investigator_role_of']
            if pi_uri not in grant['pi_uris']:
                grant['pi_uris'].append(pi_uri)
                grant['role_uris'][pi_uri] = role_uri
        if 'co_principal_investigator_role_of' in role:
            coi_uri = role['co_principal_investigator_role_of']
            if coi_uri not in grant['coi_uris']:
                grant['coi_uris'].append(coi_uri)
                grant['role_uris'][coi_uri] = role_uri
        if 'investigator_role_of' in role:
            inv_uri = role['investigator_role_of']
            if inv_uri not in grant['inv_uris']:
                grant['inv_uris'].append(inv_uri)
                grant['role_uris'][inv_uri] = role_uri

    # deref the investigators

    if get_investigators == True:
        for role_uri in grant['contributing_role_uris']:
            role = get_role(role_uri)
            if 'co_principal_investigator_role_of' in role:
                person = \
                    get_person(role['co_principal_investigator_role_of'])
                person['role'] = 'co_principal_investigator'
                grant['investigators'].append(person)
            if 'principal_investigator_role_of' in role:
                person = \
                    get_person(role['principal_investigator_role_of'])
                person['role'] = 'principal_investigator'
                grant['investigators'].append(person)
            if 'investigator_role_of' in role:
                person = \
                    get_person(role['investigator_role_of'])
                person['role'] = 'investigator'
                grant['investigators'].append(person)
    return grant

def make_ufid_dictionary(debug=False):
    """
    Make a dictionary for people in UF VIVO.  Key is UFID.  Value is URI.
    """
    query = tempita.Template("""
    SELECT ?x ?ufid WHERE
    {
    ?x ufVivo:ufid ?ufid .
    }""")
    query = query.substitute()
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0], \
            result["results"]["bindings"][1]
    #
    ufid_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        ufid = b['ufid']['value']
        uri = b['x']['value']
        ufid_dictionary[ufid] = uri
        i = i + 1
    return ufid_dictionary

def find_person(ufid, ufid_dictionary):
    """
    Given a UFID, and a dictionary, find the person with that UFID.  Return True
    and URI if found. Return False and None if not found
    """
    try:
        uri = ufid_dictionary[ufid]
        found = True
    except:
        uri = None
        found = False
    return [found, uri]

def make_webpage_rdf(full_text_uri, \
    uri_type="http://vivo.ufl.edu/ontology/vivo-ufl/FullTextURL", \
    link_anchor_text="PubMed Central Full Text Link", rank="1", \
    harvested_by="Python PubMed 1.0"):
    """
    Given a uri, create a web page entity with the uri, rank and
    anchor text, harvested_by specified
    """
    if full_text_uri is None:
        return ["", None]
    full_text_url_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{webpage_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#URLLink"/>
        <rdf:type rdf:resource="{{uri_type}}"/>
        <vivo:linkURI>{{full_text_uri}}</vivo:linkURI>
        <vivo:rank>{{rank}}</vivo:rank>
        <vivo:linkAnchorText>{{link_anchor_text}}</vivo:linkAnchorText>
        <ufVivo:harvestedBy>{{harvested_by}}</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)
    webpage_uri = get_vivo_uri()
    harvest_datetime = make_harvest_datetime()
    rdf = full_text_url_rdf_template.substitute(webpage_uri=webpage_uri, \
        full_text_uri=full_text_uri, \
        rank=rank, \
        uri_type=uri_type, \
        link_anchor_text=link_anchor_text, \
        harvested_by=harvested_by, \
        harvest_datetime=harvest_datetime)
    return [rdf, webpage_uri]

