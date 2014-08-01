#!/usr/bin/env/python

"""
    vivogrants.py -- useful functions for working with grants in VIVO

    See CHANGELOG.md for history

    To Do:
    --  write test functions
    --  move to modern sntax
    --  get rid of tempita
    --  remove count and i from dictionary functions
    --  update for VIVO-ISF
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.0"

def improve_grant_title(s):
    """
    DSP uses a series of abbreviations to fit grant titles into limited text
    strings.  Funding agencies often restrict the length of grant titles and
    faculty often clip their titles to fit in available space.  Here we reverse
    the process and lengthen the name for readability
    """
    if s == "":
        return s
    if s[len(s)-1] == ',':
        s = s[0:len(s)-1]
    if s[len(s)-1] == ',':
        s = s[0:len(s)-1]
    s = s.lower() # convert to lower
    s = s.title() # uppercase each word
    s = s + ' '   # add a trailing space so we can find these abbreviated
                  # words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @") # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace(",", " !") # might be two commas in input
    t = t.replace("-", " #")
    t = t.replace("'S ", "'s ")
    t = t.replace("2-blnd ", "Double-blind ")
    t = t.replace("2blnd ", "Double-blind ")
    t = t.replace("A ", "a ")
    t = t.replace("Aav ", "AAV ")
    t = t.replace("Aca ", "Academic ")
    t = t.replace("Acad ", "Academic ")
    t = t.replace("Acp ", "ACP ")
    t = t.replace("Acs ", "ACS ")
    t = t.replace("Act ", "Acting ")
    t = t.replace("Adj ", "Adjunct ")
    t = t.replace("Adm ", "Administrator ")
    t = t.replace("Admin ", "Administrative ")
    t = t.replace("Adv ", "Advisory ")
    t = t.replace("Advanc ", "Advanced ")
    t = t.replace("Aff ", "Affiliate ")
    t = t.replace("Affl ", "Affiliate ")
    t = t.replace("Ahec ", "AHEC ")
    t = t.replace("Aldh ", "ALDH ")
    t = t.replace("Alk1 ", "ALK1 ")
    t = t.replace("Alumn Aff ", "Alumni Affairs ")
    t = t.replace("Amd3100 ", "AMD3100 ")
    t = t.replace("And ", "and ")
    t = t.replace("Aso ", "Associate ")
    t = t.replace("Asoc ", "Associate ")
    t = t.replace("Assoc ", "Associate ")
    t = t.replace("Ast ", "Assistant ")
    t = t.replace("Ast #G ", "Grading Assistant ")
    t = t.replace("Ast #R ", "Research Assistant ")
    t = t.replace("Ast #T ", "Teaching Assistant ")
    t = t.replace("Bpm ", "BPM ")
    t = t.replace("Brcc ", "BRCC ")
    t = t.replace("Cfo ", "Chief Financial Officer ")
    t = t.replace("Cio ", "Chief Information Officer ")
    t = t.replace("Clin ", "Clinical ")
    t = t.replace("Clncl ", "Clinical ")
    t = t.replace("Cms ", "CMS ")
    t = t.replace("Cns ", "CNS ")
    t = t.replace("Cncr ", "Cancer ")
    t = t.replace("Co ", "Courtesy ")
    t = t.replace("Cog ", "COG ")
    t = t.replace("Communic ", "Communications ")
    t = t.replace("Compar ", "Compare ")
    t = t.replace("Coo ", "Chief Operating Officer ")
    t = t.replace("Copd ", "COPD ")
    t = t.replace("Cpb ", "CPB ")
    t = t.replace("Crd ", "Coordinator ")
    t = t.replace("Ctr ", "Center ")
    t = t.replace("Cty ", "County ")
    t = t.replace("Dbl-bl ", "Double-blind ")
    t = t.replace("Dbl-blnd ", "Double-blind ")
    t = t.replace("Dbs ", "DBS ")
    t = t.replace("Dev ", "Development ")
    t = t.replace("Devel ", "Development ")
    t = t.replace("Dist ", "Distinguished ")
    t = t.replace("Dna ", "DNA ")
    t = t.replace("Doh ", "DOH ")
    t = t.replace("Doh/cms ", "DOH/CMS ")
    t = t.replace("Double Blinded ", "Double-blind ")
    t = t.replace("Double-blinded ", "Double-blind ")
    t = t.replace("Dpt-1 ", "DPT-1 ")
    t = t.replace("Dtra0001 ", "DTRA0001 ")
    t = t.replace("Dtra0016 ", "DTRA-0016 ")
    t = t.replace("Educ ", "Education ")
    t = t.replace("Eff/saf ", "Safety and Efficacy ")
    t = t.replace("Emer ", "Emeritus ")
    t = t.replace("Emin ", "Eminent ")
    t = t.replace("Enforce ", "Enforcement ")
    t = t.replace("Eng ", "Engineer ")
    t = t.replace("Environ ", "Environmental ")
    t = t.replace("Epr ", "EPR ")
    t = t.replace("Eval ", "Evaluation ")
    t = t.replace("Ext ", "Extension ")
    t = t.replace("Fdot ", "FDOT ")
    t = t.replace("Fdots ", "FDOT ")
    t = t.replace("Fhtcc ", "FHTCC ")
    t = t.replace("Finan ", "Financial ")
    t = t.replace("Fla ", "Florida ")
    t = t.replace("Fllw ", "Follow ")
    t = t.replace("For ", "for ")
    t = t.replace("G-csf ", "G-CSF ")
    t = t.replace("Gen ", "General ")
    t = t.replace("Gis ", "GIS ")
    t = t.replace("Gm-csf ", "GM-CSF ")
    t = t.replace("Grad ", "Graduate ")
    t = t.replace("Hcv ", "HCV ")
    t = t.replace("Hiv ", "HIV ")
    t = t.replace("Hiv-infected ", "HIV-infected ")
    t = t.replace("Hiv/aids ", "HIV/AIDS ")
    t = t.replace("Hlb ", "HLB ")
    t = t.replace("Hlth ", "Health ")
    t = t.replace("Hou ", "Housing ")
    t = t.replace("Hsv-1 ", "HSV-1 ")
    t = t.replace("I/ii ", "I/II ")
    t = t.replace("I/ucrc ", "I/UCRC ")
    t = t.replace("Ica ", "ICA ")    
    t = t.replace("Icd ", "ICD ")
    t = t.replace("Ieee ", "IEEE ")
    t = t.replace("Ifas ", "IFAS ")
    t = t.replace("Igf-1 ", "IGF-1 ")
    t = t.replace("Ii ", "II ")
    t = t.replace("Ii/iii ", "II/III ")
    t = t.replace("Iii ", "III ")
    t = t.replace("In ", "in ")
    t = t.replace("Info ", "Information ")
    t = t.replace("Inter-vention ", "Intervention ")
    t = t.replace("Ipa ", "IPA ")
    t = t.replace("Ipm ", "IPM ")
    t = t.replace("Ippd ", "IPPD ")
    t = t.replace("Ips ", "IPS ")
    t = t.replace("It ", "Information Technology ")
    t = t.replace("Iv ", "IV ")
    t = t.replace("Jnt ", "Joint ")
    t = t.replace("Lng ", "Long ")
    t = t.replace("Mgmt ", "Management ")
    t = t.replace("Mgr ", "Manager ")
    t = t.replace("Mgt ", "Management ")
    t = t.replace("Mlti ", "Multi ")
    t = t.replace("Mlti-ctr ", "Multicenter ")
    t = t.replace("Mltictr ", "Multicenter ")
    t = t.replace("Mri ", "MRI ")
    t = t.replace("Mstr ", "Master ")
    t = t.replace("Multi-center ", "Multicenter ")
    t = t.replace("Multi-ctr ", "Multicenter ")
    t = t.replace("Nih ", "NIH ")
    t = t.replace("Nmr ", "NMR ")
    t = t.replace("Nsf ", "NSF ")
    t = t.replace("Of ", "of ")
    t = t.replace("On ", "on ")
    t = t.replace("Or ", "or ")
    t = t.replace("Open-labeled ", "Open-label ")
    t = t.replace("Opn-lbl ", "Open-label ")
    t = t.replace("Opr ", "Operator ")
    t = t.replace("Phas ", "Phased ")
    t = t.replace("Php ", "PHP ")
    t = t.replace("Phs ", "PHS ")
    t = t.replace("Pk/pd ", "PK/PD ")
    t = t.replace("Pky ", "P. K. Yonge ")
    t = t.replace("Pky ", "PK Yonge ")
    t = t.replace("Plcb-ctrl ", "Placebo-controlled ")
    t = t.replace("Plcbo ", "Placebo ")
    t = t.replace("Plcbo-ctrl ", "Placebo-controlled ")
    t = t.replace("Postdoc ", "Postdoctoral ")
    t = t.replace("Pract ", "Practitioner ")
    t = t.replace("Pres5 ", "President 5 ")
    t = t.replace("Pres6 ", "President 6 ")
    t = t.replace("Prg ", "Programs ")
    t = t.replace("Prof ", "Professor ")
    t = t.replace("Prog ", "Programmer ")
    t = t.replace("Progs ", "Programs ")
    t = t.replace("Prov ", "Provisional ")
    t = t.replace("Psr ", "PSR ")
    t = t.replace("Radiol ", "Radiology ")
    t = t.replace("Rcv ", "Receiving ")
    t = t.replace("Rdmzd ", "Randomized ")
    t = t.replace("Rep ", "Representative ")
    t = t.replace("Res ", "Research ")
    t = t.replace("Ret ", "Retirement ")
    t = t.replace("Reu ", "REU ")
    t = t.replace("Rna ", "RNA ")
    t = t.replace("Rndmzd ", "Randomized ")
    t = t.replace("Roc-124 ", "ROC-124 ")
    t = t.replace("Rsch ", "Research ")
    t = t.replace("Saf ", "SAF ")
    t = t.replace("Saf/eff ", "Safety and Efficacy ")
    t = t.replace("Sbjcts ", "Subjects ")
    t = t.replace("Sch ", "School ")
    t = t.replace("Se ", "SE ")
    t = t.replace("Ser ", "Service ")
    t = t.replace("Sfwmd ", "SFWMD ")
    t = t.replace("Sle ", "SLE ")
    t = t.replace("Sntc ", "SNTC ")
    t = t.replace("Spec ", "Specialist ")
    t = t.replace("Spnsrd ", "Sponsored ")
    t = t.replace("Spv ", "Supervisor ")
    t = t.replace("Sr ", "Senior ")
    t = t.replace("Stdy ", "Study ")
    t = t.replace("Subj ", "Subject ")
    t = t.replace("Supp ", "Support ")
    t = t.replace("Supt ", "Superintendant ")
    t = t.replace("Supv ", "Supervisor ")
    t = t.replace("Svc ", "Services ")
    t = t.replace("Svcs ", "Services ")
    t = t.replace("Tch ", "Teaching ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Technol ", "Technologist ")
    t = t.replace("Teh ", "the ")
    t = t.replace("The ", "the ")
    t = t.replace("To ", "to ")
    t = t.replace("Trls ", "Trials ")
    t = t.replace("Trm ", "Term ")
    t = t.replace("Tv ", "TV ")
    t = t.replace("Uf ", "UF ")
    t = t.replace("Ufrf ", "UFRF ")
    t = t.replace("Univ ", "University ")
    t = t.replace("Us ", "US ")
    t = t.replace("Usa ", "USA ")
    t = t.replace("Vis ", "Visiting ")
    t = t.replace("Vp ", "Vice President ")
    t = t.replace("Wuft-Fm ", "WUFT-FM ")
    t = t.replace(" @", "/") # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" #", "-") # restore -
    return t[0].upper() + t[1:-1] # Take off the trailing space

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

def string_from_grant(grant):
    """
    Given a grant object, return a string representing the grant

    To Do
    Need the PI and the dates
    """
    s = ""
    if 'awarded_by' in grant:
        s = s + grant['awarded_by'] + '\n'
    if 'sponsor_award_id' in grant:
        s = s + grant['sponsor_award_id']
    if 'pi_name' in grant:
        s = s + '          ' + grant['pi_name']
    if 'award_amount' in grant:
        s = s + ' $' + grant['award_amount']
    if 'start_date' in grant:
        s = s + '          ' + grant['start_date']['date']['month'] + '/' + \
            grant['start_date']['date']['day'] + '/' + \
            grant['start_date']['date']['year']
    if 'end_date' in grant:
        s = s + ' - ' + grant['end_date']['date']['month'] + '/' + \
            grant['end_date']['date']['day'] + '/' + \
            grant['end_date']['date']['year']
    if 'title' in grant:
        s = s + '\n' + grant['title']
    return s

def make_grant_dictionary(debug=False):
    """
    Make a dictionary for grants in UF VIVO.  Key is pcn.  Value is URI.
    """
    query = tempita.Template("""
    SELECT ?uri (SAMPLE(DISTINCT ?xpcn) AS ?pcn) WHERE
    {
    ?uri rdf:type vivo:Grant .
    ?uri ufVivo:psContractNumber ?xpcn .
    }
    GROUP BY ?uri
    """)
    query = query.substitute()
    result = vt.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0], \
            result["results"]["bindings"][1]
    #
    grant_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        pcn = b['pcn']['value']
        uri = b['uri']['value']
        grant_dictionary[pcn] = uri
        i = i + 1
    return grant_dictionary

def make_sponsor_dictionary(debug=False):
    """
    Make a dictionary for sponsors in UF VIVO.  Key is Sponsor.  Value is URI.
    """
    query = tempita.Template("""
    SELECT ?x ?sponsorid WHERE
    {
    ?x rdf:type foaf:Organization .
    ?x ufVivo:sponsorID ?sponsorid .
    }""")
    query = query.substitute()
    result = vt.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0], \
            result["results"]["bindings"][1]
    #
    sponsor_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        sponsorid = b['sponsorid']['value']
        uri = b['x']['value']
        sponsor_dictionary[sponsorid] = uri
        i = i + 1
    return sponsor_dictionary

def find_sponsor(sponsorid, sponsor_dictionary):
    """
    Given a sponsorid, find the org with that sponsor.  Return True and URI
    if found.  Return false and None if not found
    """
    try:
        uri = sponsor_dictionary[sponsorid]
        found = True
    except:
        uri = None
        found = False
    return [found, uri]

def add_grant(grant_data):
    """
    Given grant data, create a grant object in VIVO.  Return the RDF and URI
    """
    ardf = ""
    grant_uri = vt.get_vivo_uri()
    [add, sub] = vt.update_resource_property(grant_uri, "rdf:type", None,
        "http://www.w3.org/2002/07/owl#Thing")
    ardf = ardf + add
    [add, sub] = vt.update_resource_property(grant_uri, "rdf:type", None,
        "http://vivoweb.org/ontology/core#Grant")
    ardf = ardf + add
    [add, sub] = update_grant(grant_uri, grant_data)
    ardf = ardf + add
    return [ardf, grant_uri]

def update_grant(grant_uri, grant_data):
    """
    Given the URI of a grant and authoritative grant data, use five case
    logic to generate addition and subtration RDF as necessary to update the
    information in VIVO to reflect the authoritative information
    """
    properties = {'title':'rdfs:label',
                  'total_award_amount':'vivo:totalAwardAmount',
                  'sponsor_award_id':'vivo:sponsorAwardId',
                  'grant_direct_costs':'vivo:grantDirectCosts',
                  'dsr_number':'ufVivo:dsrNumber',
                  'pcn':'ufVivo:psContractNumber',
                  'date_harvested':'ufVivo:dateHarvested',
                  'harvested_by':'ufVivo:harvestedBy',
                  'local_award_id':'vivo:localAwardId'}
    resources = {'administered_by_uri':'vivo:administeredBy',
                 'dti_uri':'vivo:dateTimeInterval',
                 'sponsor_uri':'vivo:grantAwardedBy'}

    ardf = ""
    srdf = ""
    grant = vt.get_grant(grant_uri)

    # Update properties

    for property in sorted(properties.keys()):
        if property in grant:
            vivo_value = grant[property]
            if vivo_value == "":
                vivo_value = None
        else:
            vivo_value = None
        if property in grant_data:
            source_value = grant_data[property]
            if source_value == "":
                source_value = None
        else:
            source_value = None
        [add, sub] = vt.update_data_property(grant_uri, properties[property],
                                         vivo_value, source_value)
        ardf = ardf + add
        srdf = srdf + sub

    # Update resources

    for resource in sorted(resources.keys()):
        if resource in grant:
            vivo_value = grant[resource]
            if vivo_value == "":
                vivo_value = None
        else:
            vivo_value = None
        if resource in grant_data:
            source_value = grant_data[resource]
            if source_value == "":
                source_value = None
        else:
            source_value = None
        [add, sub] = vt.update_resource_property(grant_uri, resources[resource],
                                         vivo_value, source_value)
        ardf = ardf + add
        srdf = srdf + sub

    # Update the roles

    investigator_types = [\
        ['pi_uris', \
        'http://vivoweb.org/ontology/core#PrincipalInvestigatorRole', \
        'core:principalInvestigatorRoleOf',\
        'core:hasPrincipalInvestigatorRole'],\
        ['coi_uris', \
        'http://vivoweb.org/ontology/core#CoPrincipalInvestigatorRole', \
        'core:co-PrincipalInvestigatorRoleOf',\
        'core:hasCo-PrincipalInvestigatorRole'], \
        ['inv_uris',
        'http://vivoweb.org/ontology/core#InvestigatorRole', \
        'core:investigatorRoleOf',\
        'core:hasInvestigatorRole']\
        ]
    for itype, role_type, role_property, person_role in investigator_types:
        uri_case = {}
        for uri in grant_data[itype]:
            uri_case[uri] = uri_case.get(uri, 0) + 1
        for uri in grant[itype]:
            uri_case[uri] = uri_case.get(uri, 0) + 2
        for uri in uri_case:
            if uri_case[uri] == 3:

                # in VIVO and DSP.  Nothing to do

                continue

            elif uri_case[uri] == 2:

                # in VIVO only. Remove the appropriate contributing role and
                # the references to the role from the grant and investigator

                role_uri = grant['role_uris'][uri]
                sub = vt.remove_uri(role_uri)
                srdf = srdf + sub

            else:

                # in DSP only. Assert a new role with appropriate investigator
                # type and uri.  Point the grant at the new role.  Reverse
                # links are supplied by the inferencer

                role_uri = vt.get_vivo_uri()
                [add, sub] = vt.update_resource_property(role_uri, "rdf:type",
                    None, "http://www.w3.org/2002/07/owl#Thing")
                ardf = ardf + add
                [add, sub] = vt.update_resource_property(role_uri, "rdf:type",
                    None, "http://vivoweb.org/ontology/core#Role")
                ardf = ardf + add
                srdf = srdf + sub
                [add, sub] = vt.update_resource_property(role_uri, "rdf:type",
                    None, "http://vivoweb.org/ontology/core#ResearcherRole")
                ardf = ardf + add
                srdf = srdf + sub
                [add, sub] = vt.update_resource_property(role_uri, "rdf:type",
                    None, "http://vivoweb.org/ontology/core#InvestigatorRole")
                ardf = ardf + add
                srdf = srdf + sub
                [add, sub] = vt.update_resource_property(role_uri, "rdf:type",
                    None, role_type)
                ardf = ardf + add
                srdf = srdf + sub
                [add, sub] = vt.update_resource_property(role_uri, role_property,
                    None, uri)
                ardf = ardf + add
                srdf = srdf + sub
                [add, sub] = vt.update_resource_property(role_uri,
                    "vivo:dateTimeInterval",
                    None, grant_data['dti_uri'])
                ardf = ardf + add
                srdf = srdf + sub
                [add, sub] = vt.update_resource_property(grant_uri, \
                    "vivo:contributingRole", None, role_uri)
                ardf = ardf + add
                srdf = srdf + sub
                [add, sub] = vt.update_resource_property(role_uri, \
                    "vivo:roleContributesTo", None, grant_uri)
                ardf = ardf + add
                srdf = srdf + sub
                [add, sub] = vt.update_resource_property(uri, \
                    person_role, None, role_uri)
                ardf = ardf + add
                srdf = srdf + sub

    return [ardf, srdf]



