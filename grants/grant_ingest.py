#!/usr/bin/env/python

"""
    grant-ingest.py: Given grant data from the Division of Sponsored Programs,
    compare to VIVO.  Comparison is made on peoplesoft contract number (pcn)
    Then create addition and subtraction RDF for VIVO to manage
    the following entities:

    grants -- add and update.  Will create sub-awards as grants if needed
    funding org -- update only.  Grant ingest does not create funding orgs
    people (PI, Co-I, Key Personnel) -- update only.  Grant ingest does not
        create people
    connecting roles -- add
    administering org -- update only.  Grant ingest does not create UF orgs.

    There are three cases:

    Case 1: The grant is in DSP, but not in VIVO.  The grant will be added.
    Case 2: The grant is in VIVO, but not in DSP.  The grant will be untouched.
    Case 3: The grant is in both DSP and VIVO.  The grant will be updated.

    Version 0.0 2013-10-06 MC
     -- Read DSP data and grant data from VIVO.  Compare. Identify and
        tabulate cases.
    Version 0.1 2013-12-11 MC
    --  Handles sponsors and administering departments, date harvest and
        harvested by
    Version 0.2 2014-01-04 MC
    --  Reads lists of ufids for PIs, CO-Is and Investigators.  Resolves to
        URIs.  get_grant does the same by dereferencing roles to the people
        in the roles. Handles each set of roles -- pi, coi, inv -- into one
        of three cases -- role is the same in VIVO and DSP, role is in VIVO
        only, role is in DSP only. Code runs to completion.  XML has been
        validated.
    Version 0.3 2014-01-07 MC
    --  improve_grant_title improved to expand abbreviations commonly found
        in grant titles
    Version 0.4 2014-02-26 MC
    --  Update CSV file format for DSP data
    --  Improved abbreviation handling in grant titles
    --  Improved error reporting and handling
    --  All log entries are datetime stamped
    --  Get file_name for DSP data from command line
    --  Derive other file names from the DSP file name.
    --  Improved eror reporting and handling
    --  All log entries are datetime stamped
    Version 0.5 2014-03-13 MC
    --  Fix bug in role removal for investigators
    --  Fix bug in SponsorAwardID
    --  Add additional grant title improvements
    Version 0.6 2014-03-29 MC
    --  Add support for xml:lang, dataype and non-ascii characters in RDF/XML
    Version 0.7 2014-04-06 MC
    --  Add support for UTF-8
    --  Improvements to improve_grant_titles -- alphabeticized, more small
        words lower cased
    Version 0.8 2014-05-04 MC
    --  Default data file name is now vivo_grants.txt
    --  VIVO tools 1.55 escapes RDF before handling by xmlcharreplace for
        final ascii

    Future
    --  Make person_add file for people not found
    --  Add -v parameter to command line to route log to stdout
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.8"

from datetime import datetime
import random # for testing purposes, select subsets of records to process
import tempita
import sys
import os
import vivotools as vt
import codecs

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

def make_date_dictionary(datetime_precision="vivo:yearPrecision",
                              debug=False):
    """
    Given a VIVO datetime precision, return a dictionary of the URI for each
    date value.
    """
    date_dictionary = {}
    query = tempita.Template("""
    SELECT ?uri ?dt
    WHERE {
      ?uri vivo:dateTimePrecision {{datetime_precision}} .
      ?uri vivo:dateTime ?dt .
    }""")
    query = query.substitute(datetime_precision=datetime_precision)
    result = vt.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0], \
            result["results"]["bindings"][1]
    #
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        if datetime_precision == "vivo:yearPrecision":
            dt = b['dt']['value'][0:4]
            dtv = datetime.strptime(dt, '%Y')
        elif datetime_precision == "vivo:yearMonthPrecision":
            dt = b['dt']['value'][0:7]
            dtv = datetime.strptime(dt, '%Y-%m')
        elif datetime_precision == "vivo:yearMonthDayPrecision":
            dt = b['dt']['value'][0:10]
            dtv = datetime.strptime(dt, '%Y-%m-%d')
        uri = b['uri']['value']
        date_dictionary[dtv] = uri
        i = i + 1
    return date_dictionary

def make_datetime_interval_dictionary(debug=False):
    """
    Make a dictionary for datetime intervals in UF VIVO.
    Key is concatenation of start and end uris.  Value is URI.
    """
    query = tempita.Template("""
    SELECT ?uri ?starturi ?enduri
    WHERE
    {
        ?uri vivo:end ?enduri .
        ?uri vivo:start ?starturi .
    }
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
    datetime_interval_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        uri = b['uri']['value']
        if 'starturi' in b:
            start_uri = b['starturi']['value']
        else:
            start_uri = "None"
        if 'enduri' in b:
            end_uri = b['enduri']['value']
        else:
            end_uri = "None"
        key = start_uri+end_uri
        datetime_interval_dictionary[key] = uri
        i = i + 1
    return datetime_interval_dictionary

def find_datetime_interval(start_uri, end_uri, datetime_dictionary):
    """
    Given start and end uris for dates, find an interval with that pair of
    dates, find the org with that sponsor.  Return True and URI
    Return false and None if not found
    """
    if start_uri == None or start_uri == "":
        start_key = "None"
    else:
        start_key = start_uri

    if end_uri == None or end_uri == "":
        end_key = "None"
    else:
        end_key = end_uri

    try:
        uri = datetime_interval_dictionary[start_key+end_key]
        found = True
    except:
        uri = None
        found = False
    return [found, uri]

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

def make_dsp_dictionary(file_name="grant_data.csv", debug=False):
    """
    Read a CSV file with grant data from the Division of Sponsored Programs.
    Create a dictionary with one entry per PeopleSoft Contract Number (pcn).

    If multiple rows exist in the data for a particular pcn,
    the last row will be used in the dictionary
    """
    dsp_dictionary = {}
    ardf = ""
    error_count = 0
    dsp_data = vt.read_csv(file_name)
    for row in dsp_data.keys():
        any_error = False

        if row % 100 == 0:
            print row
            
        pcn = dsp_data[row]['AwardID']

        # Simple attributes

        dsp_data[row]['pcn'] = pcn
        dsp_data[row]['title'] = improve_grant_title(dsp_data[row]['Title'])
        dsp_data[row]['sponsor_award_id'] = dsp_data[row]['SponsorAwardID']
        dsp_data[row]['local_award_id'] = dsp_data[row]['AwardID']
        dsp_data[row]['harvested_by'] = 'Python Grants ' + __version__
        dsp_data[row]['date_harvested'] = str(datetime.now())

        # Award amounts

        try:
            total = float(dsp_data[row]['TotalAwarded'])
            dsp_data[row]['total_award_amount'] = dsp_data[row]['TotalAwarded']
        except ValueError:
            total = None
            print >>exc_file, pcn, "Total Award Amount", \
                dsp_data[row]['TotalAwarded'], "invalid number"
            any_error = True

        try:
            direct = float(dsp_data[row]['DirectCosts'])
            dsp_data[row]['grant_direct_costs'] = dsp_data[row]['DirectCosts']
        except ValueError:
            direct = None
            print >>exc_file, pcn, "Grant Direct Costs", \
                dsp_data[row]['DirectCosts'], "invalid number"
            any_error = True

        if total is not None and total < 0:
            print >>exc_file, pcn, "Total Award Amount", \
                dsp_data[row]['total_award_amount'], "must not be negative"
            any_error = True

        if direct is not None and direct < 0:
            print >>exc_file, pcn, "Grant Direct Costs", \
                dsp_data[row]['grant_direct_costs'], "must not be negative"
            any_error = True

        if direct is not None and total is not None and total < direct:
            print >>exc_file, pcn, "Total Award Amount", \
                dsp_data[row]['total_award_amount'],\
                "must not be less than Grant Direct Costs", \
                dsp_data[row]['grant_direct_costs']
            any_error = True

        # Admin department

        [found, administered_by_uri] = vt.find_deptid(dsp_data[row]['DeptID'], \
            deptid_dictionary)
        if found:
            dsp_data[row]['administered_by_uri'] = administered_by_uri
        else:
            print >>exc_file, pcn, "DeptID", dsp_data[row]['DeptID'], \
                "not found in VIVO"
            any_error = True

        # Sponsor

        [found, sponsor_uri] = find_sponsor(dsp_data[row]['SponsorID'], \
            sponsor_dictionary)
        if found:
            dsp_data[row]['sponsor_uri'] = sponsor_uri
        else:
            print >>exc_file, pcn, "Sponsor", dsp_data[row]['SponsorID'], \
                "not found in VIVO"
            any_error = True

        # Start and End dates

        try:
            start_date = datetime.strptime(dsp_data[row]['StartDate'],\
                '%m/%d/%Y')
            if start_date in date_dictionary:
                start_date_uri = date_dictionary[start_date]
            else:
                [add, start_date_uri] = \
                    vt.make_datetime_rdf(start_date.isoformat())
                date_dictionary[start_date] = start_date_uri
                ardf = ardf + add
        except ValueError:
            print >>exc_file, pcn, "Start date", dsp_data[row]['StartDate'], \
                "invalid"
            start_date = None
            start_date_uri = None
            any_error = True

        try:
            end_date = datetime.strptime(dsp_data[row]['EndDate'],\
                '%m/%d/%Y')
            if end_date in date_dictionary:
                end_date_uri = date_dictionary[end_date]
            else:
                [add, end_date_uri] = \
                    vt.make_datetime_rdf(end_date.isoformat())
                date_dictionary[end_date] = end_date_uri
                ardf = ardf + add
        except ValueError:
            print >>exc_file, pcn, "End date", dsp_data[row]['EndDate'], \
                "invalid"
            end_date = None
            end_date_uri = None
            any_error = True


        if end_date is not None and start_date is not None and \
            end_date < start_date:
            print >>exc_file, pcn, "End date", dsp_data[row]['EndDate'], \
                "before start date", dsp_data[row]['StartDate']
            any_error = True

        [found, dti_uri] = find_datetime_interval(start_date_uri, \
            end_date_uri, datetime_interval_dictionary)
        if found:
            dsp_data[row]['dti_uri'] = dti_uri
        else:
            if start_date_uri is not None or end_date_uri is not None:
                [add, dti_uri] = vt.make_dt_interval_rdf(start_date_uri, \
                    end_date_uri)
                datetime_interval_dictionary[start_date_uri+\
                    end_date_uri] = dti_uri
                ardf = ardf + add
                dsp_data[row]['dti_uri'] = dti_uri

        # Investigators

        investigator_names = [['pi_uris', 'PI'], ['coi_uris', 'CoPI'],\
            ['inv_uris', 'Inv']]
        for uri_type, ufid_type in investigator_names:
            dsp_data[row][uri_type] = []
            if dsp_data[row][ufid_type] != '' and \
                dsp_data[row][ufid_type] != None:
                ufid_list = dsp_data[row][ufid_type].split(',')
                for ufid in ufid_list:
                    [found, uri] = vt.find_person(ufid, ufid_dictionary)
                    if found:
                        dsp_data[row][uri_type].append(uri)
                    else:
                        print >>exc_file, pcn, ufid_type, ufid, \
                            "not found in VIVO"
                        any_error = True

        # If there are any errors in the data, we can't add the grant

        if any_error:
            error_count = error_count + 1
            continue

        # Assign row to dictionary entry

        dsp_dictionary[pcn] = dsp_data[row]
    return [ardf, error_count, dsp_dictionary]

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

# Driver program starts here

debug = False

# Fraction of records to be processed. Set to 1.0 to process all

sample = 1.00

if len(sys.argv) > 1:
    dsp_file_name = str(sys.argv[1])
else:
    dsp_file_name = "vivo_grants.txt"
file_name, file_extension = os.path.splitext(dsp_file_name)

add_file = codecs.open(file_name+"_add.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
sub_file = codecs.open(file_name+"_sub.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
log_file = codecs.open(file_name+"_log.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
exc_file = codecs.open(file_name+"_exc.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')

print >>log_file, datetime.now(), "Grant Ingest Version", __version__
print >>log_file, datetime.now(), "VIVO Tools Version", vt.__version__

add_file.write(vt.rdf_header())
sub_file.write(vt.rdf_header())

print >>log_file, datetime.now(), "Make VIVO DeptID Dictionary"
deptid_dictionary = vt.make_deptid_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO deptid dictionary has ", \
    len(deptid_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO UFID Dictionary"
ufid_dictionary = vt.make_ufid_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO ufid dictionary has ", \
    len(ufid_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO Sponsor Dictionary"
sponsor_dictionary = make_sponsor_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO sponsor dictionary has ", \
    len(sponsor_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO Date Dictionary"
date_dictionary = \
    make_date_dictionary(datetime_precision="vivo:yearMonthDayPrecision",\
    debug=debug)
print >>log_file, datetime.now(), "VIVO date dictionary has ", \
    len(date_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO Datetime Interval Dictionary"
datetime_interval_dictionary = make_datetime_interval_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO datetime interval dictionary has ", \
    len(datetime_interval_dictionary), " entries"


print >>log_file, datetime.now(), "Make VIVO Grant Dictionary"
grant_dictionary = make_grant_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO grant dictionary has ", \
    len(grant_dictionary), " entries"

#   Read the DSP data and make a dictionary ready to be processed.  The
#   dictionary will contain data values and references to VIVO entities
#   (people and dates) sufficient to create or update each grant.  New dates
#   and datetime intervals might be needed.  The make_dsp_dictionary process
#   creates these and returns RDF for them to be added to VIVO.

print >>log_file, datetime.now(), "Read DSP Grant Data from", \
      dsp_file_name
[ardf, error_count, dsp_dictionary] = \
    make_dsp_dictionary(file_name=dsp_file_name,\
    debug=debug)
if ardf != "":
    add_file.write(ardf)
print >>log_file, datetime.now(), "DSP data has ", len(dsp_dictionary), \
    " valid entries"
print >>log_file, datetime.now(), "DSP data has ", error_count, \
    " invalid entries.  See exception file for details"

#   Loop through the DSP data and the VIVO data, adding each pcn to the
#   action report.  1 for DSP only.  2 for VIVO only.  3 for both

action_report = {}
for pcn in dsp_dictionary.keys():
    action_report[pcn] = action_report.get(pcn, 0) + 1
for pcn in grant_dictionary.keys():
    action_report[pcn] = action_report.get(pcn, 0) + 2

print >>log_file, datetime.now(), "Action report has ", len(action_report), \
    "entries"

#   Loop through the action report for each pcn.  Count and log the cases

n1 = 0
n2 = 0
n3 = 0
for pcn in action_report.keys():
    if action_report[pcn] == 1:
        n1 = n1 + 1
    elif action_report[pcn] == 2:
        n2 = n2 + 1
    else:
        n3 = n3 + 1

print >>log_file, datetime.now(), n1,\
    " Grants in DSP only.  These will be added to VIVO."
print >>log_file, datetime.now(), n2,\
    " Grants in VIVO only.  No action will be taken."
print >>log_file, datetime.now(), n3,\
    " Grants in both DSP and VIVO.  Will be updated as needed."

# Set up complete.  Now loop through the action report. Process each pcn

print >>log_file, datetime.now(), "Begin Processing"
row = 0
for pcn in sorted(action_report.keys()):
    row = row + 1
    if row % 100 == 0:
        print row

    ardf = ""
    srdf = ""
    r = random.random()  # random floating point between 0.0 and 1.0
    if r > sample:
        continue

    if action_report[pcn] == 1:

        #   Case 1: DSP Only. Add Grant to VIVO.

        print >>log_file, datetime.now(), pcn, "Case 1: Add   "

        grant_data = dsp_dictionary[pcn]
        [add, grant_uri] = add_grant(grant_data)
        ardf = ardf + add

    elif action_report[pcn] == 2:

        # Case 2: VIVO Only.  Nothing to do.

        pass

    else:

        #   Case 3: DSP and VIVO. Update grant.

        print >>log_file, datetime.now(), pcn, "Case 3: Update"

        grant_uri = grant_dictionary[pcn]
        grant_data = dsp_dictionary[pcn]

        [add, sub] = update_grant(grant_uri, grant_data)
        ardf = ardf + add
        srdf = srdf + sub

    if ardf != "":
        add_file.write(ardf)
    if srdf != "":
        sub_file.write(srdf)

#   Done processing the Grants.  Wrap-up

add_file.write(vt.rdf_footer())
sub_file.write(vt.rdf_footer())
print >>log_file, datetime.now(), "End Processing"

add_file.close()
sub_file.close()
log_file.close()
exc_file.close()
