#!/usr/bin/env/python
""" vivopeople.py -- A library of useful things for working with people in VIVO

    Write test scripts for:
    
    repair_email
    get_position_type
    improve_jobcode_decription
    get_telephone
    get_name
    add_position
    add_vcard
    add_person
    update_person

    Update:
    
    get_degree
    make_ufid_disctionary
    find_person (rename find_ufid)
    
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
            name['honorific_prefix'] = o
        if p == "http://www.w3.org/2006/vcard/ns#honorificSuffix":
            name['honorific_suffix'] = o
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
            position['dti_uri'] = o
            datetime_interval = get_datetime_interval(o)
            position['datetime_interval'] = datetime_interval
            if 'start_date' in datetime_interval:
                position['start_date'] = datetime_interval['start_date']
            if 'end_date' in datetime_interval:
                position['end_date'] = datetime_interval['end_date']  
        i = i + 1

    return position

def add_position(person_uri, position):
    """
    Given a person_uri and a position dictionary containing the attributes
    of a position, generate the RDF necessary to create the position,
    associate it with the person and assign its attributes.
    """
    from vivofoundation import assert_resource_property
    from vivofoundation import assert_data_property
    from vivofoundation import add_dti
    from vivofoundation import get_vivo_uri
    
    ardf = ""
    position_uri = get_vivo_uri()
    dti = {'start' : position.get('start_date',None),
           'end': position.get('end_date',None)}
    [add, dti_uri] = add_dti(dti)
    ardf = ardf + add
    ardf = ardf + assert_resource_property(position_uri,
            'rdf:type', position['position_type'])
    ardf = ardf + assert_resource_property(position_uri,
            'rdfs:label', position['position_label'])
    ardf = ardf + assert_resource_property(position_uri,
            'vivo:dateTimeInterval', dti_uri)
    ardf = ardf + assert_resource_property(position_uri,
            'vivo:relates', person_uri)
    ardf = ardf + assert_resource_property(position_uri,
            'vivo:relates', position['position_orguri'])
    
    return [ardf, position_uri]

def add_vcard(person_uri, vcard):
    """
    Given a person_uri and a vcard dictionary of items on the vcard,
    generate ther RDF necessary to create the vcard, associate it with
    the person, and associate attributes to the vcard.

    The person_uri will be associated to the vcard and the vcard may have
    any number of single entry entities to references.  The single_entry
    table controls the processing of these entities.

    The name entity is a special case. All values are attrbuted to the name
    entity.

    The single_entry table contains some additional keys for future use
    Both the name table and the single entry table are easily extensible to
    handle additional name attributes and additional single entry entities
    respectively.
    """
    
    from vivofoundation import assert_resource_property
    from vivofoundation import assert_data_property
    from vivofoundation import get_vivo_uri
    from vivofoundation import untag_predicate
    
    single_entry = {
        'primary_email': {'resource':'vcard:hasEmail','type':'vcard:Email',
                          'pred':'vcard:email'},
        'email': {'resource':'vcard:hasEmail','type':'vcard:Email',
                  'pred':'vcard:email'},
        'fax': {'resource':'vcard:hasTelephone','type':'vcard:Fax',
                'pred':'vcard:telephone'},
        'telephone': {'resource':'vcard:hasTelephone','type':'vcard:Telephone',
                      'pred':'vcard:telephone'},
        'preferred_title': {'resource':'vcard:hasTitle','type':'vcard:Title',
                            'pred':'vcard:title'},
        'title': {'resource':'vcard:hasTitle','type':'vcard:Title',
                  'pred':'vcard:title'}
    }
    name_table = {
        'first_name' : 'vcard:givenName',
        'last_name' : 'vcard:familyName',
        'middle_name' : 'vcard:additionalName',
        'name_prefix' : 'vcard:honoraryPrefix',
        'name_suffix' : 'vcard:honorarySuffix'
        }
    ardf = ""
    vcard_uri = get_vivo_uri()
    ardf = ardf + assert_resource_property(vcard_uri, 'rdf:type',
                                           untag_predicate('vcard:Individual'))
    ardf = ardf + assert_resource_property(person_uri, 'obo:ARG2000028',
                                           vcard_uri) # hasContactInfo
    ardf = ardf + assert_resource_property(vcard_uri, 'obo:ARG2000029',
                                           person_uri) # contactInfoOf

    # Create the name entity and attach to vcard. For each key in the
    # name_table, assert its value to the name entity

    name_uri = get_vivo_uri()
    ardf = ardf + assert_resource_property(name_uri, 'rdf:type',
                                           untag_predicate('vcard:Name'))
    ardf = ardf + assert_resource_property(vcard_uri, 'vcard:hasName',
                                           name_uri)
    for key in vcard.keys():
        if key in name_table:
            pred = name_table[key]
            val = vcard[key]
            ardf = ardf + assert_data_property(name_uri,
                pred, val)            

    # Process single entry vcard bits of info:
    #   Go through the keys in the vcard.  If it's a single entry key, then
    #   create it.  Assign the data vaue and link the vcard to the single
    #   entry entity

    for key in vcard.keys():
        if key in single_entry:
            val = vcard[key]
            entry = single_entry[key]
            entry_uri = get_vivo_uri()
            ardf = ardf + assert_resource_property(entry_uri,
                'rdf:type', untag_predicate(entry['type']))
            ardf = ardf + assert_data_property(entry_uri,
                entry['pred'], val)
            ardf = ardf + assert_resource_property(vcard_uri,
                entry['resource'], entry_uri)
    return [ardf, vcard_uri]

def update_vcard(vivo_vcard, source_vcard):
    """
    Given a vivo vcard and a source vccard, generate the add and sub rdf
    necesary to update vivo the the values ion the source
    """
    
    from vivofoundation import update_entity
    from vivofoundation import update_data_property
    from vivofoundation import get_vivo_uri
    from vivofoundation import assert_data_property
    from vivofoundation import assert_resource_property
    from vivofoundation import untag_predicate

    ardf = ""
    srdf = ""

    # Update the name entity

    name_keys = {
        'given_name' : {'predicate':'vcard:givenName','action':'literal'},
        'family_name' : {'predicate':'vcard:familyName',
                       'action':'literal'},
        'additional_name' : {'predicate':'vcard:additionalName',
                         'action':'literal'},
        'honorific_prefix' : {'predicate':'vcard:honorificPrefix',
                         'action':'literal'},
        'honorific_suffix' : {'predicate':'vcard:honorificSuffix',
                         'action':'literal'}
    }

    # Update name entity
    
    if 'name' in source_vcard and 'name' not in vivo_vcard:
        name_uri = get_vivo_uri()
        ardf = ardf + assert_resource_property(name_uri, 'rdf:type',
                                           untag_predicate('vcard:Name'))
        ardf = ardf + assert_resource_property(vcard['vcard_uri'],
            'vcard:hasName', name_uri)
        vivo_vcard['name_uri'] = name_uri
        vivo_vcard['name'] = {}
    if 'name' in source_vcard:
        vivo_vcard['name']['uri'] = vivo_vcard['name_uri']
        [add, sub] = update_entity(vivo_vcard['name'],
                                   source_vcard['name'], name_keys)
        ardf = ardf + add
        srdf = srdf + sub

    #   Update title

    if 'title' in source_vcard and 'title' not in vivo_vcard:
        title_uri = get_vivo_uri()
        ardf = ardf + assert_resource_property(title_uri, 'rdf:type',
                                           untag_predicate('vcard:Title'))
        ardf = ardf + assert_resource_property(vivo_vcard['vcard_uri'],
            'vcard:hasTitle', title_uri)
        vivo_vcard['title_uri'] = title_uri
        vivo_vcard['title'] = None
    if 'title' in source_vcard:
        [add, sub] = update_data_property(vivo_vcard['title_uri'],
            'vcard:title', vivo_vcard['title'], source_vcard['title'])
        ardf = ardf + add
        srdf = srdf + sub

    #   Update phone.  For now, assert a phone.  We can't seem to tell which
    #   phone is to be "updated".  If VIVO has telephones a and b, and the
    #   source says the phone number is c, what is the appropriate operation?
    #   We will just pick a phone and update it to c.  If ther person has zero
    #   or one phones, everything is fine.  These are the most likely cases.
    #   And in the above two phone case, we have a 50-50 chance of doing the
    #   right thing.  So perhaps 1% of people will be effected adversely by
    #   the code that follows.

    if 'phone' in source_vcard and source_vcard['phone'] is not None:
        if 'telephones' not in vivo_vcard or vivo_vcard['telephones'] == []:
            telephone_uri = get_vivo_uri()
            ardf = ardf + assert_resource_property(vivo_vcard['vcard_uri'],
                'vcard:hasTelephone', telephone_uri)
            ardf = ardf + assert_resource_property(telephone_uri,
                'rdf:type', untag_predicate('vcard:telephone'))
            telephone_value = None
        else:
            for telephone in vivo_vcard['telephones']:
                if telephone['telephone_type'] == 'Telephone':
                    telephone_uri = telephone['telephone_uri']
                    telephone_value = telephone['telephone_number']
                    continue
        [add, sub] = update_data_property(telephone_uri,
            'vcard:telephone', telephone_value, source_vcard['phone'])
        ardf = ardf + add
        srdf = srdf + sub

    #   Analogous processing with analogous comments for a fax number

    if 'fax' in source_vcard and source_vcard['fax'] is not None:
        if 'telephones' not in vivo_vcard or vivo_vcard['telephones'] == []:
            telephone_uri = get_vivo_uri()
            ardf = ardf + assert_resource_property(vivo_vcard['vcard_uri'],
                'vcard:hasTelephone', telephone_uri)
            ardf = ardf + assert_resource_property(telephone_uri,
                'rdf:type', untag_predicate('vcard:Fax'))
            telephone_value = None
        else:
            for telephone in vivo_vcard['telephones']:
                if telephone['telephone_type'] == 'Fax':
                    telephone_uri = telephone['telephone_uri']
                    telephone_value = telephone['telephone_number']
                    continue
        [add, sub] = update_data_property(telephone_uri,
            'vcard:telephone', telephone_value, source_vcard['fax'])
        ardf = ardf + add
        srdf = srdf + sub

    #   Analogous processing with analogous comments for an email address

    if 'primary_email' in source_vcard and \
       source_vcard['primary_email'] is not None:
        if 'email_addresses' not in vivo_vcard or \
           vivo_vcard['email_addresses'] == []:
            email_uri = get_vivo_uri()
            ardf = ardf + assert_resource_property(vivo_vcard['vcard_uri'],
                'vcard:hasEmail', email_uri)
            ardf = ardf + assert_resource_property(email_uri,
                'rdf:type', untag_predicate('vcard:Email'))
            email_value = None
        else:
            email_uri = email_addresses[0]['email_uri']
            email_value = email_address[0]['email_address']
        [add, sub] = update_data_property(email_uri,
            'vcard:email', email_value, source_vcard['primary_email'])
        ardf = ardf + add
        srdf = srdf + sub
    
    return [ardf, srdf]

def update_position(vivo_position, source_position):
    """
    Given a position in VIVO and a position from an authoritative source,
    update the VIVO position to reflect the source
    """
    from vivofoundation import update_entity
    from vivofoundation import update_resource_property
    from vivofoundation import add_dti

    #   Note: We do not label positions with
    #   harvest attributes.
    
    update_keys = {
        'position_label': {'predicate':'rdfs:label','action':'literal'},
        'position_rank': {'predicate':'vivo:rank','action':'literal'},
        'position_type': {'predicate':'rdf:type','action':'resource'},
        'position_orguri': {'predicate':'vivo:relates','action':'resource'},
        'person_uri': {'predicate':'vivo:relates','action':'resource'}
        }
    ardf = ""
    srdf = ""
    [add, sub] = update_entity(vivo_position, source_position, update_keys)
    ardf = ardf + add
    srdf = srdf + sub

    #  Compare the start and end dates of vivo and source.  If not
    #  equal, replace the vivo referent with a new datetime interval
    #  referent.  If a datetime interval already exists in VIVO with
    #  the same start and end values, no attempt is made to find and
    #  reuse it.  A separate process, absolute_dates, can be used to
    #  find and merge duplicate dates.

    if vivo_position.get('start_date', None) != \
       source_position.get('start_date', None) or \
       vivo_position.get('end_date', None) != \
       source_position.get('end_date', None):
        [add, dti_uri] = \
            add_dti({'start':source_position.get('start_date', None),
                                 'end':source_position.get('end_date', None)})
        ardf = ardf + add
        [add, sub] = update_resource_property(vivo_position['uri'],
            'vivo:dateTimeInterval', vivo_position.get('dti_uri',None), dti_uri)
    return [ardf, srdf]

def add_person(person):
    """
    Add a person to VIVO.  The person structure may have any number of
    elements.  These elements may represent direct assertions (label,
    ufid, homeDept), vcard assertions (contact info, name parts),
    and/or position assertions (title, tye, dept, start, end dates)
    """
    from vivofoundation import assert_data_property
    from vivofoundation import assert_resource_property
    from vivofoundation import untag_predicate
    from vivofoundation import get_vivo_uri
    
    ardf = ""
    person_uri = get_vivo_uri()

    # Add direct assertions

    person_type = person['person_type']
    ardf = ardf + assert_resource_property(person_uri, 'rdf:type', person_type)
    ardf = ardf + assert_resource_property(person_uri, 'rdf:type',
                        untag_predicate('ufv:UFEntity'))
    ardf = ardf + assert_resource_property(person_uri, 'rdf:type',
                        untag_predicate('ufv:UFCurrentEntity'))

    direct_data_preds = {'ufid':'ufv:ufid',
                         'privacy_flag':'ufv:privacyFlag',
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
        if key in person.keys():
            vcard[key] = person[key]
    [add, vcard_uri] = add_vcard(person_uri, vcard)
    ardf = ardf + add

    # Add Position Assertions

    position = {}
    for key in ['start_date', 'position_label', 'end_date', 'position_orguri',
                'position_type']:
        if key in person.keys():
            position[key] = person[key]

    [add, position_uri] = add_position(person_uri, position)
    ardf = ardf + add
    
    return [ardf, person_uri]

def update_person(vivo_person, source_person):
    """
    Given a data structure representing a person in VIVO, and a data
    structure representing the same person with data values from source
    systems, generate the ADD and SUB RDF necessary to update the VIVO
    person's data values to the corresponding values in the source

    These data structures are NOT comparable.  The VIVO data structure is the
    structure returned by get_person and reflects the hieriarchical and
    repeating nature of data in VIVO.  The source data structure is flat,
    representing the single-valued input file

    Key values are grouped into three sets -- direct (attributes of the
    person directly), vcard attributes and position attributes

    There are only 22 attributes.  How difficult could it be to update
    them in VIVO?
    """
    from vivopeople import get_position_uris
    from vivopeople import get_position
    from vivopeople import update_position
    from vivopeople import update_vcard
    from vivofoundation import update_entity
    import json
    
    direct_key_table = {
    'privacy_flag': {'predicate': 'ufv:privacyFlag',
                    'action': 'literal'},
    'homedept_uri': {'predicate': 'ufv:homeDept',
                    'action': 'resource'},
    'display_name': {'predicate': 'rdfs:label',
                    'action': 'literal'},
    'ufid': {'predicate': 'ufv:ufid',
                    'action': 'literal'},
    'gatorlink': {'predicate': 'ufv:gatorlink',
                    'action': 'literal'},
    'person_type': {'predicate': 'rdf:type',
                    'action': 'literal'},
    'date_harvested': {'predicate': 'ufv:dateHarvested',
                    'action': 'literal'},
    'harvested_by': {'predicate': 'ufv:harvestedBy',
                    'action': 'literal'}
    }

    vcard_names = ['given_name', 'honorfic_prefix', 'honorific_suffix',
                   'additional_name', 'family_name']
    vcard_flat = ['fax',  'phone', 'title']
    position_keys = ['position_label', 'end_date', 'position_type',
                     'position_orguri', 'start_date']
    
    ardf = ""
    srdf = ""

    #   Update some things.  This never goes well
    #   First.  The vivo entity has to have a key value 'uri'
    #   Second.  If the source data is not an HR position, it does not
    #   have authoritative information to update the person type

    person_uri = vivo_person['person_uri']
    vivo_person['uri'] = person_uri
    if source_person['hr_position'] == False:
        del direct_key_table['person_type']

    [add, sub] = update_entity(vivo_person, source_person, \
                               direct_key_table)
    ardf = ardf + add
    srdf = srdf + sub

    #   Update vcard and its assertions

    vivo_vcard = vivo_person['vcard']
    source_vcard = {'name':{}}
    source_vcard['person_uri'] = person_uri
    for key in vcard_names:
        if key in source_person:
            source_vcard['name'][key] = source_person[key]
    for key in vcard_flat:
        if key in source_person:
            source_vcard[key] = source_person[key]

    print "VIVO Vcard:\n",json.dumps(vivo_vcard, indent=4)
    print "Source Vcard:\n",json.dumps(source_vcard, indent=4)
    
    [add, sub] = update_vcard(vivo_vcard, source_vcard)
    ardf = ardf + add
    srdf = srdf + sub

    #   Update position.  Examine each position.  If you find a match on
    #   department and title, update it.  Otherwise add it.

    source_position = {}
    for key in position_keys:
        source_position[key] = source_person[key]
    source_position['person_uri'] = person_uri
    position_uris = get_position_uris(person_uri)
    updated = False
    for position_uri in position_uris:
        vivo_position = get_position(position_uri)
        print "\nVIVO position",vivo_position
        print "\nSource position",source_position
        if vivo_position.get('position_type',None) == \
           source_position.get('position_type',None) \
            and vivo_position.get('position_orguri',None) == \
            source_position.get('position_orguri',None):
            [add, sub] = update_position(vivo_position, source_position)
            updated = True
            ardf = ardf + add
            srdf = srdf + sub
            continue
    if updated == False:
        [add, sub] = add_position(person_uri, source_position)
        ardf = ardf + add
        srdf = srdf + sub
    
    return [ardf, srdf]

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
