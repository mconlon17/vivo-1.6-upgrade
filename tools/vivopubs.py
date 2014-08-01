#!/usr/bin/env/python
""" vivopubs.py -- A library of useful things for working with VIVO pubs

    See CHANGELOG for a running account of the changes to vivopubs
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "2.00"

def abbrev_to_words(s):
    """
    Text is often abbreviated in the names of publishers and journals.
    This helper function takes a string s and returns an improved version
    with abbreviations replaced by words.  Handle cosmetic improvements.
    Replace special characters with escape versions for RDF
    """
    t = s.replace("Dept ", "Department ")
    t = t.replace("Soc ", "Society ")
    t = t.replace("Med ", "Medical ")
    t = t.replace("Natl ", "National ")
    t = t.replace("Univ ", "University ")
    t = t.replace("Publ ", "Publishers ")
    t = t.replace("Am ", "American ")
    t = t.replace("Assoc ", "Association ")
    t = t.replace("Acad ", "Academy ")
    t = t.replace("Of ", "of ")
    t = t.replace("In ", "in ")
    t = t.replace("As ", "as ")
    t = t.replace("Ieee ", "IEEE ")
    t = t.replace("A ", "a ")
    t = t.replace("For ", "for ")
    t = t.replace("And ", "and ")
    t = t.replace("The ", "the ")
    t = t.replace("Inst ", "Institute ")
    t = t.replace("Sci ", "Science ")
    t = t.replace("Amer ", "American ")
    t = t.replace("'S ", "'s ")
    t = t.replace("Ii ", "II ")
    t = t.replace("Iii ", "III ")
    t = t.replace("Iv ", "IV ")
    t = t.replace("\&", "&amp;")
    t = t.replace("<", "&lt;")
    t = t.replace(">", "&gt;")

    # Returned value will always start with an upper case letter

    t = t[0].upper() + t[1:]
    return t

def make_journal_uri(value):
    """
    Given a bibtex publication value, return the journal uri from VIVO.
    Three cases:  1) There is no journal name in the bibtex.  We return
    an empty URI.  2) We find the journal in VIVO, we return the
    URI of the journal in VIVO. 3) We don't find the journal, so we
    return a new URI.
    """

    # get the name of the journal from the data.  Fix it up a bit before
    # trying to find

    try:
        journal_name = value.fields['journal'].title()+ " "
        journal_name = abbrev_to_words(journal_name)
        journal_name = journal_name[0:-1]
        issn = value.fields['issn']
        document['journal'] = journal_name
        document['issn'] = issn
    except:
        journal_uri = ""
        journal_name = "No Journal"
        create = False
        return [create, journal_name, journal_uri]

    # now we are ready to look for the journal -- first in the
    # journal_report (journals we have already
    # processed in this run, and if not found there, then in the journal
    # dictionary created from VIVO

    if journal_name in journal_report:
        create = False
        journal_uri = journal_report[journal_name][1]
        journal_report[journal_name][2] = journal_report[journal_name][2] + 1
    else:
        [found, uri] = vivotools.find_journal(issn, journal_dictionary)
        if not found:

            # Will need to create

            create = True
            journal_uri = vivotools.get_vivo_uri()
        else:

            # Found in VIVO

            create = False
            journal_uri = uri
        journal_report[journal_name] = [create, journal_uri, 1]

    return [create, journal_name, journal_uri]

def make_publisher_rdf(value):
    """
    Given a bibtex publication value, create the RDF for a publisher
    """
    publisher_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdfs:label>{{publisher}}</rdfs:label>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Publisher"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Organization"/>
        <ufVivo:harvestedBy>Python Pubs version 1.3</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)

    # get the name of the publisher from the data.  Fix it up a bit
    # before trying to find

    try:
        publisher = value.fields['publisher'].title() + " "
        publisher = abbrev_to_words(publisher)
        publisher = publisher[0:-1]
    except:
        uri = ""
        publisher = "No publisher"
        create = False
        rdf = "\n<!-- No publisher found for this publication." +\
            " No RDF necessary -->"
        return [create, publisher, uri, rdf]

    #  now we are ready to look for the publisher

    if publisher in publisher_report:
        create = False
        uri = publisher_report[publisher][1]
        publisher_report[publisher][2] = \
            publisher_report[publisher][2] + 1
        rdf = "\n<!-- " + publisher + " found at uri to be created " +\
            uri + "  No RDF necessary -->"
    else:
        [found, uri] = vivotools.find_publisher(publisher,\
            publisher_dictionary)
        if not found:

            # Publisher not found.  We need to add one.

            create = True
            uri = vivotools.get_vivo_uri()
            harvest_datetime = vivotools.make_harvest_datetime()
            rdf = "\n<!-- Publisher RDF for " + publisher + " -->"
            rdf = rdf + publisher_template.substitute(uri=uri,\
                publisher=publisher, harvest_datetime=harvest_datetime)
            publisher_report[publisher] = [create, uri, 1]
        else:

            # Publisher found.  return the uri of the publisher

            create = False
            rdf = "\n<!-- " + publisher + " found in VIVO at uri " +\
                uri + "  No RDF necessary -->"
            publisher_report[publisher] = [create, uri, 1]
    return [create, publisher, uri, rdf]

def make_journal_rdf(value, journal_create, journal_name, journal_uri):
    """
    Given a bibtex publication value, create the RDF for the journal of
    the journal of the publication if the journal is not already in VIVO
    """
    journal_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{journal_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdfs:label>{{journal_name}}</rdfs:label>
        <rdf:type rdf:resource="http://purl.org/ontology/bibo/Journal"/>
        {{if len(issn) > 0 :}}
            <bibo:issn>{{issn}}</bibo:issn>
        {{endif}}
        <ufVivo:harvestedBy>Python Pubs version 1.3</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)
    if not journal_create:
        rdf = "\n<!-- " + journal_name + " found at uri " +\
            journal_uri + "  No RDF necessary -->"
    else:

        # Not found. get the issn of the journal

        try:
            issn = value.fields['issn']
        except:
            issn = ""
        harvest_datetime = vivotools.make_harvest_datetime()
        rdf = "\n<!-- Journal RDF for " + journal_name + " -->"
        rdf = rdf + journal_template.substitute(journal_uri=journal_uri,\
            journal_name=journal_name, issn=issn,\
            harvest_datetime=harvest_datetime)
    return [rdf, journal_uri]

def make_publisher_journal_rdf(publisher_uri, journal_uri):
    """
    Create the assertions PublisherOf and PublishedBy between a
    publisher and a journal
    """
    publisher_journal_template = tempita.Template("""
    <rdf:Description rdf:about="{{publisher_uri}}">
        <core:publisherOf  rdf:resource="{{journal_uri}}"/>
    </rdf:Description>
    <rdf:Description rdf:about="{{journal_uri}}">
        <core:publisher rdf:resource="{{publisher_uri}}"/>
    </rdf:Description>
    """)
    rdf = ""
    harvest_datetime = vivotools.make_harvest_datetime()
    rdf = rdf + "\n<!-- Publisher/Journal assertions for " + publisher +\
        " and " + journal_name + " -->"
    rdf = rdf + publisher_journal_template.substitute(\
        publisher_uri=publisher_uri, journal_uri=journal_uri,
        harvest_datetime=harvest_datetime)
    return rdf

def name_parts(author):
    """
    Given the name of an author, break it in to first, middle, last and assign a
    case number to the type of name information we have

    Case 0 last name only
    Case 1 last name, first initial
    Case 2 last name, first name
    Case 3 last name, first initial, middle initial
    Case 4 last name, first initial, middle name
    Case 5 last name, first name, middle initial
    Case 6 last name, first name, middle name
    """
    name_cut = author.split(',')
    last = name_cut[0]
    if len(name_cut) > 1:
        rest = name_cut[1]
        rest = rest.replace(',', '')
        rest = rest.replace('.', '')
        name_list = rest.split()
        name_list.insert(0, last)
    else:
        name_list = [last]
    if len(name_list) >= 3:
        last = name_list[0]
        first = name_list[1]
        middle = name_list[2]
        if len(first) == 1 and len(middle) == 1:
            case = 3
        if len(first) == 1 and len(middle) > 1:
            case = 4
        if len(first) > 1 and len(middle) == 1:
            case = 5
        if len(first) > 1 and len(middle) > 1:
            case = 6
    elif len(name_list) == 2:
        last = name_list[0]
        first = name_list[1]
        middle = ""
        if len(first) == 1:
            case = 1
        if len(first) > 1:
            case = 2
    else:
        last = name_list[0]
        first = ""
        middle = ""
        case = 0
    result = [last, first, middle, case]
    return result

def update_dict(dict, key, val):
    """
    return a list of the results of dict[key] with val appended
    """
    try:
        l = dict[key]
    except:
        l = []
    l.append(val)
    return l

def make_people_dictionaries(debug=False):
    """
    Get all the UFEntity people from VIVO and build seven dictionaries:
    put each person in as many dictionaries as they can be (between 1
    and 7) based on the presence of their name parts in VIVO.  A last
    name part is required to be in the SPARQL result set.
    """
    query = tempita.Template("""
    SELECT ?x ?fname ?lname ?mname WHERE
    {
    ?x rdf:type foaf:Person .
    ?x foaf:lastName ?lname .
    ?x rdf:type ufVivo:UFEntity .
    OPTIONAL {?x core:middleName ?mname .}
    OPTIONAL {?x foaf:firstName ?fname .}
    }""")
    query = query.substitute()
    result = vivotools.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0],\
            result["results"]["bindings"][1]

    # make the dictionaries
    #
    # Case 0 last name only
    # Case 1 last name, first initial
    # Case 2 last name, first name
    # Case 3 last name, first initial, middle initial
    # Case 4 last name, first initial, middle name
    # Case 5 last name, first name, middle initial
    # Case 6 last name, first name, middle name

    case0_dict = {}
    case1_dict = {}
    case2_dict = {}
    case3_dict = {}
    case4_dict = {}
    case5_dict = {}
    case6_dict = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        lname = b['lname']['value']
        uri = b['x']['value']
        try:
            fname = b['fname']['value']
        except:
            fname = ""
        try:
            mname = b['mname']['value']
        except:
            mname = ""
        if len(fname) > 0 and len(mname) > 0:

            # seven cases here

            k0 = vivotools.key_string(lname)
            k1 = vivotools.key_string(lname + ':' + fname[0])
            k2 = vivotools.key_string(lname + ':' + fname)
            k3 = vivotools.key_string(lname + ':' + fname[0] +\
                ':' + mname[0])
            k4 = vivotools.key_string(lname + ':' + fname[0] +\
                ':' + mname)
            k5 = vivotools.key_string(lname + ':' + fname + ':' +\
                mname[0])
            k6 = vivotools.key_string(lname + ':' + fname + ':' +\
                mname)
            case0_dict[k0] = update_dict(case0_dict, k0, uri)
            case1_dict[k1] = update_dict(case1_dict, k1, uri)
            case2_dict[k2] = update_dict(case2_dict, k2, uri)
            case3_dict[k3] = update_dict(case3_dict, k3, uri)
            case4_dict[k4] = update_dict(case4_dict, k4, uri)
            case5_dict[k5] = update_dict(case5_dict, k5, uri)
            case6_dict[k6] = update_dict(case6_dict, k6, uri)
        elif len(fname) > 0 and len(mname) == 0:

            # three cases here

            k0 = vivotools.key_string(lname)
            k1 = vivotools.key_string(lname + ':' + fname[0])
            k2 = vivotools.key_string(lname + ':' + fname)
            case0_dict[k0] = update_dict(case0_dict, k0, uri)
            case1_dict[k1] = update_dict(case1_dict, k1, uri)
            case2_dict[k2] = update_dict(case2_dict, k2, uri)
        elif len(fname) == 0 and len(mname) == 0:

            # one case here

            k0 = vivotools.key_string(lname)
            case0_dict[k0] = update_dict(case0_dict, k0, uri)
        i = i + 1
    return [case0_dict, case1_dict, case2_dict, case3_dict, case4_dict,\
        case5_dict, case6_dict]

def find_author(author):
    """
    Given an author name in the form last, first middle with middle
    and/or first eitehr blank or single character with or with periods,
    find the name in the appropriate case dictionary.  The
    case dictionaries are prepared using make_people_dictionaries
    """
    [lname, fname, mname, case] = name_parts(author)
    [case0_dict, case1_dict, case2_dict, case3_dict, case4_dict,\
        case5_dict, case6_dict] = dictionaries
    if case == 0:
        k0 = vivotools.key_string(lname)
        result = case0_dict.get(k0, [])
    elif case == 1:
        k1 = vivotools.key_string(lname + ':' + fname[0])
        result = case1_dict.get(k1, [])
    elif case == 2:
        k2 = vivotools.key_string(lname + ':' + fname)
        result = case2_dict.get(k2, [])
    elif case == 3:
        k3 = vivotools.key_string(lname + ':' + fname[0] +':' + mname[0])
        result = case3_dict.get(k3, [])
    elif case == 4:
        k4 = vivotools.key_string(lname + ':' + fname[0] + ':' + mname)
        result = case4_dict.get(k4, [])
    elif case == 5:
        k5 = vivotools.key_string(lname + ':' + fname + ':' + mname[0])
        result = case5_dict.get(k5, [])
    else:
        k6 = vivotools.key_string(lname + ':' + fname + ':' + mname)
        result = case6_dict.get(k6, [])
    return result

def uf_affiliation(affiliation):
    """
    Given an affiliation string, return true if the affiliation is for
    UF, False if not
    """

    #  Is this list of authors a UF list?

    k1 = affiliation.find("Gainesville")
    k2 = affiliation.find("Univ Fl")
    k3 = affiliation.find("UNIV FL")
    k4 = affiliation.find("UF Col Med")
    k5 = affiliation.find("UF Coll Med")
    isUF_affiliation = k1 >= 0 or k2 >= 0 or k3 >= 0 or k4 >= 0 or\
        k5 >= 0
    return isUF_affiliation

def make_authors(value, debug=False):
    """
    Given a bibtex publication value, return a dictionary, one entry per
    author.  The key is the author name, the value is a list = order,
    corresponding author (t/f), UF author (t/f), corporate
    author (t/f), last, first, middle and case.  Case is an integer
    from 0 to 6 indicating how much of a name we actually have.  See
    name_parts for description.

    To do:  Add code to improve parsing of similar names.  The current
    code can be confused if author names are subsets, such as Childs, A.
    and Childs, A. Baker
    """
    authors = {}
    try:
        author_names = value.fields['author'].split(' and ')
    except:
        author_names = []
    try:
        affiliation_text = value.fields['affiliation']
    except:
        affiliation_text = ""
    if len(author_names) > MAX_AUTHORS:
        other_authors = ";".join(author_names[MAX_AUTHORS:])
        author_names = author_names[0:MAX_AUTHORS]
        author_names.append(other_authors)

    #  prepare the affiliation_list

    order = 0
    for author in author_names:
        order = order + 1
        if order > MAX_AUTHORS:
            authors[author] = [order, False, False, True, author,
                "", "", None]
            break
        authors[author] = [order, False, False, False] + name_parts(author)
        k = affiliation_text.find(author)
        auth = author
        auth = author.replace('.', '+')
        if auth == author:
            continue # nothing to do, there are no periods to replace
        else:
            while k >= 0:
                affiliation_text = affiliation_text.replace(author, "/" +\
                    auth + "/", 1)
                k = affiliation_text.find(author)
    affiliation_list = affiliation_text.split('.')
    affiliation_list = affiliation_list[0:-1]

    # find the corresponding author. Corresponding authors are not listed by
    # full name. Typically they are listed by last name, first initial, but
    # other variants are used. Here we match only on the last name, which
    # could result in an error if two authors have the same last name and
    # the first one is not the corresponding author

    for affiliation in affiliation_list:
        for author in author_names:
            last_name = authors[author][4]
            if affiliation.find(last_name) >= 0 and\
                affiliation.find('(Reprint Author)') >= 0:
                authors[author][1] = True

                # while we are here, check to see if this is a UF affiliation.
                # If it is, mark the found corresponding author as a UF
                # author.  This handles a nasty edge case where the
                # corresponding author might have a UF affiliation in the
                # corresponding author affiliation, but a non-UF affiliation
                # in the regular affiliation fields.

                if uf_affiliation(affiliation):
                    authors[author][2] = True
                break

    # find the UF authors.  For each affiliation, look to see if it is a UF
    # affiliation. if it is, all authors found in it are UF authors.  If not,
    # all authors are not UF authors.  If one person is found in two
    # affiliations and is a UF author in either one, the the author is a UF
    # author.
    #
    # if all the affiliations are UF affiliations, then all the authors are
    # UF authors

    count_uf_affiliations = 0
    for a in affiliation_list:
        if uf_affiliation(a):
            count_uf_affiliations = count_uf_affiliations + 1
    if len(affiliation_list) == count_uf_affiliations:

        # all affiliations are UF, so all authors are UF

        for author in author_names:
            authors[author][2] = True
    else:

        # Not all the affiliations are UF, so we need to check each one

        for a in affiliation_list:
            affiliation = a.replace('+', '.')
            if uf_affiliation(affiliation):
                if len(author_names) == 1:
                    authors[author_names[0]][2] = True
                else:
                    for author in author_names:
                        if debug:
                            print "...Looking for>" + author +\
                                "< in UF affiliation>" + affiliation + "<"
                        if affiliation.find(author) >= 0:
                            authors[author][2] = True
    return authors

def count_uf_authors(authors, debug=False):
    """
    Given an author structure from make_authors, return the count of UF authors
    """
    count = 0
    for value in authors.values():
        if value[2]:
            count = count + 1
    if debug:
        print "UF author count is ", count
    return count

def update_author_report(authors):
    """
    Given an authors structure, update the author_report for each author
    """

    # accumulate all the authors in a structure for reporting

    for author, value in authors.items():
        if author in author_report:
            result = author_report[author]
            result[len(result.keys())+1] = value
            author_report[author] = result
        else:
            author_report[author] = {1:value}
    return

def make_author_rdf(value):
    """
    Given a bibtex publication value, create the RDF for the authors
    of the publication.  Some authors may need to be created, while others
    may be found in VIVO.

    For each author:
      Is author UF?
      Yes:
        How many authors at UF have this name?
        0:  Add the author, add to notify list
        1:  Get the URI for inclusion in the authorship
        2:  Punt the whole publication to the manual disambiguation list
      No:
        Create a new stub for the author (corporate or single).  Return the
        URI for authorship.
    If no UF authors, punt the whole publication to the error list
    Otherwise produce RDF for authors to be added
    Return the URIs of all authors (found or added)
    """
    author_template = tempita.Template("""
    <rdf:Description rdf:about="{{author_uri}}">
        <rdfs:label>{{author_name}}</rdfs:label>
        {{if len(first) > 0:}}
            <foaf:firstName>{{first}}</foaf:firstName>
        {{endif}}
        {{if len(middle)>0:}}
            <core:middleName>{{middle}}</core:middleName>
        {{endif}}
        <foaf:lastName>{{last}}</foaf:lastName>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>
        {{if isUF:}}
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFEntity"/>
        {{endif}}
        <ufVivo:harvestedBy>Python Pubs version 1.3</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)
    corporate_author_template = tempita.Template("""
    <rdf:Description rdf:about="{{author_uri}}">
        <rdfs:label>{{group_name}}</rdfs:label>
        <core:overview>{{author_name}}</core:overview>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Group"/>
        <ufVivo:harvestedBy>Python Pubs version 1.3</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)
    rdf = ""
    authors = make_authors(value)
    for author, value in authors.items():
        isUF = value[2]
        isCorporate = value[3]
        if isUF:
            if author in author_report:

                # UF author previously found in this Python Pubs run.
                # Use the URI previously assigned to this author

                author_uri = author_report[author][1][-1]
                action = "Found UF"
                rdf = rdf + "\n<!-- Previously found UF author " + author +\
                    " with uri " + author_uri + " -->"
            else:

                # Look for the author in VIVO

                result = find_author(author)

                # How many people did you find with this author name?

                count = len(result)
                if count == 0:

                    # create a new UF author, and notify

                    author_uri = vivotools.get_vivo_uri()
                    action = "Make UF "
                    harvest_datetime = vivotools.make_harvest_datetime()
                    rdf = rdf + "\n<!-- UF author stub RDF for " + author +\
                        " at uri " + author_uri + " and notify -->"
                    rdf = rdf + author_template.substitute(isUF=isUF,\
                        author_uri=author_uri, author_name=author,\
                        first=value[5], middle=value[6], last=value[4],\
                        harvest_datetime=harvest_datetime)
                elif count == 1:

                    # Bingo! Disambiguated UF author. Add URI

                    author_uri = result[0]
                    action = "Found UF"
                    rdf = rdf + "\n<!-- Found UF author " + author +\
                        " with uri " + author_uri + " -->"
                else:

                    # More than 1 UF author has this name.  Add to the
                    # disambiguation list

                    author_uri = ";".join(result)
                    action = "Disambig"
                    rdf = rdf + "\n<!-- " + str(count) +\
                        " UF people found with name " + author +\
                        " Disambiguation required -->"
        elif isCorporate:

            # Corporate author

            author_uri = vivotools.get_vivo_uri()
            action = "Corp Auth"
            group_name = title + " Authorship Group"
            harvest_datetime = vivotools.make_harvest_datetime()
            rdf = rdf + "\n<!-- Corporate author stub RDF for " + author +\
                " at uri " + author_uri + " -->"
            rdf = rdf + corporate_author_template.substitute(\
                author_uri=author_uri, author_name=author,\
                group_name=group_name, harvest_datetime=harvest_datetime)
        else:

            # Non UF author -- create a stub

            author_uri = vivotools.get_vivo_uri()
            action = "non UF  "
            harvest_datetime = vivotools.make_harvest_datetime()
            rdf = rdf + "\n<!-- Non-UF author stub RDF for " + author +\
                " at uri " + author_uri + " -->"
            rdf = rdf + author_template.substitute(isUF=isUF,\
                author_uri=author_uri, author_name=author,\
                first=value[5], middle=value[6], last=value[4],\
                harvest_datetime=harvest_datetime)

        # For each author, regardless of the cases above, record whether this
        # author needs to be created and
        # what URI refers to the author (a new URI if author will be created,
        # otherwise an existing URI)

        authors[author].append(action)
        authors[author].append(author_uri)
    return [rdf, authors]

def make_authorship_rdf(authors, publication_uri):
    """
    Given the authors structure (see make_authors), and the uri of the
    publication, create the RDF for the authorships of the publication.
    Authorships link authors to publications, supporting the many-to-many
    relationship between authors and publications.
    """
    authorship_template = tempita.Template("""
    <rdf:Description rdf:about="{{authorship_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Authorship"/>
        <core:linkedAuthor rdf:resource="{{author_uri}}"/>
        <core:linkedInformationResource rdf:resource="{{publication_uri}}"/>
        <core:authorRank>{{author_rank}}</core:authorRank>
        <core:isCorrespondingAuthor>{{corres_auth}}</core:isCorrespondingAuthor>
    </rdf:Description>
    """)
    rdf = ""
    authorship_uris = {}
    for author, value in authors.items():
        author_rank = value[0]
        authorship_uri = vivotools.get_vivo_uri()
        authorship_uris[author] = authorship_uri
        if value[8] == "Disambig":
            author_uri = value[9].split(";")[0] # take first URI if multiple
        else:
            author_uri = value[9]
        corres_auth = value[1]
        harvest_datetime = vivotools.make_harvest_datetime()
        rdf = rdf + "\n<!-- Authorship for " + author + "-->"
        rdf = rdf + authorship_template.substitute(\
            authorship_uri=authorship_uri, author_uri=author_uri,\
            publication_uri=publication_uri, author_rank=author_rank,\
            corres_auth=corres_auth, harvest_datetime=harvest_datetime)
    return [rdf, authorship_uris]

def make_author_in_authorship_rdf(authors, authorship_uris):
    """
    Given the authorship_uris (see make_authorship_rdf), and the uri of the
    publication, create the RDF for the AuthorInAuthorship relationships of
    people to authorships.
    """
    author_in_authorship_template = tempita.Template("""
    <rdf:Description rdf:about="{{author_uri}}">
        <core:authorInAuthorship rdf:resource="{{authorship_uri}}"/>
    </rdf:Description>
    """)
    rdf = ""
    for author, value in authors.items():
        if value[8] == "Disambig":
            author_uri = value[9].split(";")[0] # take first URI if multiple
        else:
            author_uri = value[9]
        authorship_uri = authorship_uris[author]
        harvest_datetime = vivotools.make_harvest_datetime()
        rdf = rdf + "\n<!-- AuthorshipInAuthorship for " + author + "-->"
        rdf = rdf + author_in_authorship_template.substitute(\
            author_uri=author_uri, authorship_uri=authorship_uri,\
            harvest_datetime=harvest_datetime)
    return rdf

def make_journal_publication_rdf(journal_uri, publication_uri):
    """
    Create the assertions publicationVenueFor and hasPublicationVenue between
    a journal and a publication
    """
    journal_publication_template = tempita.Template("""
    <rdf:Description rdf:about="{{journal_uri}}">
        <core:publicationVenueFor  rdf:resource="{{publication_uri}}"/>
    </rdf:Description>
    <rdf:Description rdf:about="{{publication_uri}}">
        <core:hasPublicationVenue rdf:resource="{{journal_uri}}"/>
    </rdf:Description>
    """)
    rdf = ""
    harvest_datetime = vivotools.make_harvest_datetime()
    rdf = rdf + "\n<!-- Journal/publication assertions for " +\
        journal_name + " and " + title + " -->"
    rdf = rdf + journal_publication_template.substitute(\
        publication_uri=publication_uri, journal_uri=journal_uri,\
        harvest_datetime=harvest_datetime)
    return rdf

def map_bibtex_type(bibtex_type):
    """
    Given a bibtex_type from TR, map to a VIVO document type
    """
    map = {"article":"article",
        "book":"book",
        "booklet":"document",
        "conference":"conferencePaper",
        "inbook":"bookSection",
        "incollection":"documentPart",
        "inproceedings":"conferencePaper",
        "manual":"manual",
        "mastersthesis":"thesis",
        "misc":"document",
        "phdthesis":"thesis",
        "proceedings":"proceedings",
        "techreport":"report",
        "unpublished":"document"}
    return map.get(bibtex_type, "document")

def map_tr_types(tr_types_value, debug=False):
    """
    Given a string of TR type information, containing one or more types
    separated by semi-colons, map each one, returning a list of mapped
    values
    """
    map = {"bookreview":"review",
        "correction":"document",
        "editorial material":"editorialArticle",
        "review":"review",
        "article":"article",
        "proceedings paper":"conferencePaper",
        "newsitem":"article",
        "letter":"document",
        "theater review":"review"}
    tr_list = tr_types_value.split(";")
    if debug:
        print "tr_list", tr_list
    vivo_types = []
    for a in tr_list:
        b = a.strip()
        tr_type = b.lower()
        vivo_type = map.get(tr_type, "document")
        if len(vivo_types) == 0:
            vivo_types = [vivo_type]
        else:
            if vivo_type not in vivo_types:
                vivo_types.append(vivo_type)
    if debug:
        print vivo_types
    return vivo_types

def map_publication_types(value, debug=False):
    """
    Given a bibtex publication value, find the bibtex type and map to VIVO
    Then get the Thomson-Reuters types and map them to VIVO.
    Then merge the two lists and return all the types
    """

    # Get and map the bibtex type

    try:
        bibtex_type = value.type
    except:
        bibtex_type = "article"
    vivo_type = map_bibtex_type(bibtex_type)

    # get and map the TR types

    try:
        tr_types_value = value.fields['type']
    except:
        tr_types_value = ""
    vivo_types_from_tr = map_tr_types(tr_types_value, debug=debug)

    #  combine the values and return

    if vivo_type not in vivo_types_from_tr:
        vivo_types_from_tr.append(vivo_type)
    if debug:
        print "bibtex type", bibtex_type, "vivo type", vivo_type
        print "tr_types_value", tr_types_value, "vivo types",\
            vivo_types_from_tr
        print vivo_types_from_tr
    return vivo_types_from_tr

def make_publication_rdf(value, title, publication_uri, datetime_uri,\
        authorship_uris):
    """
    Given a bibtex publication value and previously created or found URIs,
    create the RDF for the publication itself. The publication will link to
    previously created or discovered objects, including the timestamp, the
    journal and the authorships
    """
    publication_template = tempita.Template("""
    <rdf:Description rdf:about="{{publication_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
        <rdfs:label>{{title}}</rdfs:label>
        <rdf:type rdf:resource="http://purl.org/ontology/bibo/Document"/>
        {{for type in types:}}
            {{if type=="article"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/AcademicArticle"/>
            {{endif}}
            {{if type=="book"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Book"/>
            {{endif}}
            {{if type=="document"}}
            {{endif}}
            {{if type=="conferencePaper"}}
                <rdf:type rdf:resource="http://vivoweb.org/ontology/core#ConferencePaper"/>
            {{endif}}
            {{if type=="bookSection"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/BookSection"/>
            {{endif}}
            {{if type=="documentPart"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/DocumentPart"/>
            {{endif}}
            {{if type=="manual"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Manual"/>
            {{endif}}
            {{if type=="thesis"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Thesis"/>
            {{endif}}
            {{if type=="proceedings"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Proceedings"/>
            {{endif}}
            {{if type=="report"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Report"/>
            {{endif}}
            {{if type=="review"}}
                <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Review"/>
            {{endif}}
            {{if type=="editorialArticle"}}
                <rdf:type rdf:resource="http://vivoweb.org/ontology/core#EditorialArticle"/>
            {{endif}}
        {{endfor}}
        {{if len(doi) > 0:}}
            <bibo:doi>{{doi}}</bibo:doi>
        {{endif}}
        {{if len(volume) > 0:}}
            <bibo:volume>{{volume}}</bibo:volume>
        {{endif}}
        {{if len(number) > 0:}}
            <bibo:number>{{number}}</bibo:number>
        {{endif}}
        {{if len(start) > 0:}}
            <bibo:pageStart>{{start}}</bibo:pageStart>
        {{endif}}
        {{if len(end) > 0:}}
            <bibo:pageEnd>{{end}}</bibo:pageEnd>
        {{endif}}
        {{for author,authorship_uri in authorship_uris:}}
            <core:informationResourceInAuthorship
                rdf:resource="{{authorship_uri}}"/>
        {{endfor}}
        <core:dateTimeValue rdf:resource="{{datetime_uri}}"/>
        <ufVivo:harvestedBy>Python Pubs version 1.3</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)

    # get publication attributes from the bibtex value.  In each case, use
    # a try-except construct in case the named attribute does not exist
    # in the bibtex.  Not all publications have a doi, for example

    types = map_publication_types(value)
    try:
        doi = value.fields['doi']
        document['doi'] = doi
    except:
        doi = ""
    try:
        volume = value.fields['volume']
        document['volume'] = volume
    except:
        volume = ""
    try:
        number = value.fields['number']
        document['number'] = number
    except:
        number = ""

    # Get the pages element from the bibtex.  If found, try to split it
    # into start and end

    try:
        pages = value.fields['pages']
    except:
        pages = ""
    pages_list = pages.split('-')
    try:
        start = pages_list[0]
        document['page_start'] = start
    except:
        start = ""
    try:
        end = pages_list[1]
        document['page_end'] = end
    except:
        end = ""

    # write out the head, then one line for each authorship, then the tail

    rdf = "\n<!-- Publication RDF for " + title + "-->"
    harvest_datetime = vivotools.make_harvest_datetime()
    rdf = rdf + publication_template.substitute(\
        publication_uri=publication_uri, title=title, doi=doi, volume=volume,\
        number=number, start=start, end=end, types=types,\
        datetime_uri=datetime_uri, harvest_datetime=harvest_datetime,\
        authorship_uris=authorship_uris.items())
    return rdf

def make_document_authors(authors):
    """
    Given the structure returned by make_authors, return the structure needed
    by document
    """
    author_dict = {}
    for author in authors.values():
        author_dict["{0:>10}".format(author[0])] = {'first':author[5],\
         'middle':author[6], 'last':author[4]}
    return author_dict

def make_pub_datetime(value):
    """
    Given a pybtex value structure, return the isoformat date string of the
    publication date

    To do:
    --  Return the datetime, not a string
    --  Pass in a date field, not the entire pybtex value
    """
    try:
        year = int(value.fields['year'])
    except:
        year = 2012
    try:
        m = value.fields['month'].upper()
    except:
        m = 'JAN'
    month = 1
    if m.startswith('JAN'):
        month = 1
    elif m.startswith('FEB'):
        month = 2
    elif m.startswith('MAR'):
        month = 3
    elif m.startswith('APR'):
        month = 4
    elif m.startswith('MAY'):
        month = 5
    elif m.startswith('JUN'):
        month = 6
    elif m.startswith('JUL'):
        month = 7
    elif m.startswith('AUG'):
        month = 8
    elif m.startswith('SEP'):
        month = 9
    elif m.startswith('OCT'):
        month = 10
    elif m.startswith('NOV'):
        month = 11
    elif m.startswith('DEC'):
        month = 12
    elif m.startswith('WIN'):
        month = 1
    elif m.startswith('SPR'):
        month = 4
    elif m.startswith('SUM'):
        month = 7
    elif m.startswith('FAL'):
        month = 10
    else:
        month = 1
    dt = date(year, month, 1)
    document['date'] = {'month':str(month), 'day':'1', 'year':str(year)}
    return dt.isoformat()


def get_pmid_from_doi(doi, email='mconlon@ufl.edu', tool='PythonQuery',
                      database='pubmed'):
    """
    Given a DOI, return the PMID of ther corresponding PubMed Article.  If not
    found in PubMed, return None. Adapted from
    http://simon.net.nz/articles/query-pubmed-for-citation-information-
        using-a-doi-and-python/
    """
    params = {'db':database, 'tool':tool, 'email':email, 'term': doi,
        'usehistory':'y', 'retmax':1}
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?' + \
        urllib.urlencode(params)

    # Get data from Entrez.  Retry if Entrez does not respond

    start = 2.0
    retries = 10
    count = 0
    while True:
        try:
            data = urllib.urlopen(url).read()
            xmldoc = parseString(data)
            ids = xmldoc.getElementsByTagName('Id')
            if len(ids) == 0:
                pmid = None
            else:
                pmid = ids[0].childNodes[0].data
            return pmid
        except:
            count = count + 1
            if count > retries:
                return None
            sleep_seconds = start**count
            print "<!-- Failed Entrez PMID query. Count = "+str(count)+ \
                " Will sleep now for "+str(sleep_seconds)+ \
                " seconds and retry -->"
            time.sleep(sleep_seconds) # increase the wait time with each retry


def get_pubmed_values(doi, pmid= None, debug=False):
    """
    Given the doi of a paper, return the current values (if any) for PMID,
    PMCID, Grants Cited, abstract, keywords, nihmsid, and Full_text_uri of
    the paper in PubMed Central.

    Return items in a dictionary.  Grants_cited and keywod_list are
    lists of strings.
    """
    Entrez.email = 'mconlon@ufl.edu'
    values = {}
    grants_cited = []
    keyword_list = []
    if pmid is None:
        pmid = get_pmid_from_doi(doi)
        if pmid is None:
            return {}
    else:
        values['pmid'] = pmid

    # Get record(s) from Entrez.  Retry if Entrez does not respond

    start = 2.0
    retries = 10
    count = 0
    while True:
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
            records = Entrez.parse(handle)
            break
        except:
            count = count + 1
            if count > retries:
                return {}
            sleep_seconds = start**count
            print "<!-- Failed Entrez query. Count = "+str(count)+ \
                " Will sleep now for "+str(sleep_seconds)+ \
                " seconds and retry -->"
            time.sleep(sleep_seconds) # increase the wait time with each retry

    # Find the desired attributes in the record structures returned by Entrez

    for record in records:
        if debug:
            print "Entrez record:", record
        article_id_list = record['PubmedData']['ArticleIdList']
        for article_id in article_id_list:
            attributes = article_id.attributes
            if 'IdType' in attributes:
                if attributes['IdType'] == 'pmc':
                    values["pmcid"] = str(article_id)
                if attributes['IdType'] == 'mid':
                    values["nihmsid"] = str(article_id)
        try:
            values['abstract'] = \
                record['MedlineCitation']['Article']['Abstract']\
                ['AbstractText'][0]
        except:
            pass
        try:
            keywords = record['MedlineCitation']['MeshHeadingList']
            for keyword in keywords:
                keyword_list.append(str(keyword['DescriptorName']))
            values["keyword_list"] = keyword_list
        except:
            pass
        try:
            grants = record['MedlineCitation']['Article']['GrantList']
            for grant in grants:
                grants_cited.append(grant['GrantID'])
            values["grants_cited"] = grants_cited
        except:
            pass

    # If we found a pmcid, construct the full text uri by formula

    if 'pmcid' in values:
        values["full_text_uri"] = \
            "http://www.ncbi.nlm.nih.gov/pmc/articles/" + \
            values["pmcid"].upper()+ "/pdf"
    return values

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

def make_doi_dictionary(debug=False):
    """
    Extract all the dois of documents in VIVO and organize them into a
    dictionary keyed by prepared label with value URI
    """
    query = tempita.Template("""
    SELECT ?x ?doi WHERE
    {
    ?x rdf:type bibo:Document .
    ?x bibo:doi ?doi .
    }""")
    doi_dictionary = {}
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
    doi_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        doi = b['doi']['value']
        uri = b['x']['value']
        doi_dictionary[doi] = uri
        i = i + 1
    return doi_dictionary

def make_title_dictionary(debug=False):
    """
    Extract all the titles of documents in VIVO and organize them into a
    dictionary keyed by prepared label with value URI
    """
    query = tempita.Template("""
    SELECT ?x ?label WHERE
    {
    ?x rdf:type bibo:Document .
    ?x rdfs:label ?label .
    }""")
    title_dictionary = {}
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
    title_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        title = b['label']['value']
        key = key_string(title)
        uri = b['x']['value']
        title_dictionary[key] = uri
        i = i + 1
    return title_dictionary

def find_title(title, title_dictionary):
    """
    Given a title, and a title dictionary, find the document in VIVO with that
    title.  Return True and URI if found.  Return False and None if not found
    """
    key = key_string(title)
    try:
        uri = title_dictionary[key]
        found = True
    except:
        uri = None
        found = False
    return [found, uri]

def make_publisher_dictionary(debug=False):
    """
    Extract all the publishers from VIVO and organize them into a dictionary
    keyed by prepared label with value URI
    """
    query = tempita.Template("""
    SELECT ?x ?label WHERE
    {
    ?x rdf:type core:Publisher .
    ?x rdfs:label ?label .
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
    publisher_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        publisher = b['label']['value']
        key = key_string(publisher)
        uri = b['x']['value']
        publisher_dictionary[key] = uri
        i = i + 1
    return publisher_dictionary

def find_publisher(publisher, publisher_dictionary):
    """
    Given a publisher label, and a publisher dictionary, find the publisher in
    VIVO with that label.  Return True and URI if found.  Return False and
    None if not found
    """
    key = key_string(publisher)
    try:
        uri = publisher_dictionary[key]
        found = True
    except:
        uri = None
        found = False
    return [found, uri]

def make_journal_dictionary(debug=False):
    """
    Extract all the journals from VIVO and organize them into a dictionary
    keyed by ISSN with value URI
    """
    query = tempita.Template("""
    SELECT ?x ?issn WHERE
    {
    ?x rdf:type bibo:Journal .
    ?x bibo:issn ?issn .
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
    journal_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        issn = b['issn']['value']
        uri = b['x']['value']
        journal_dictionary[issn] = uri
        i = i + 1
    return journal_dictionary

def find_journal(issn, journal_dictionary):
    """
    Given an issn, and a journal_dictinary, find the journal in VIVO with that
    UFID. Return True and URI if found.  Return False and None if not found
    """
    try:
        uri = journal_dictionary[issn]
        found = True
    except:
        uri = None
        found = False
    return [found, uri]

def catalyst_pmid_request(first, middle, last, email, debug=False):
    """
    Give an author name at the University of Florida, return the PMIDs of
    papers that are likely to be the works of the author.  The Harvard
    Catalyst GETPMIDS service is called.

    Uses HTTP XML Post request, by www.forceflow.be
    """
    request = tempita.Template("""
        <?xml version="1.0"?>
        <FindPMIDs>
            <Name>
                <First>{{first}}</First>
                <Middle>{{middle}}</Middle>
                <Last>{{last}}</Last>
                <Suffix/>
            </Name>
            <EmailList>
                <email>{{email}}</email>
            </EmailList>
            <AffiliationList>
                <Affiliation>%university of florida%</Affiliation>
                <Affiliation>%@ufl.edu%</Affiliation>
            </AffiliationList>
            <LocalDuplicateNames>1</LocalDuplicateNames>
            <RequireFirstName>false</RequireFirstName>
            <MatchThreshold>0.98</MatchThreshold>
        </FindPMIDs>""")
    HOST = "profiles.catalyst.harvard.edu"
    API_URL = "/services/GETPMIDs/default.asp"
    request = request.substitute(first=first, middle=middle, last=last, \
        email=email)
    webservice = httplib.HTTP(HOST)
    webservice.putrequest("POST", API_URL)
    webservice.putheader("Host", HOST)
    webservice.putheader("User-Agent", "Python post")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(request))
    webservice.endheaders()
    webservice.send(request)
    statuscode, statusmessage, header = webservice.getreply()
    result = webservice.getfile().read()
    if debug:
        print "Request", request
        print "StatusCode, Messgage,header", statuscode, statusmessage, header
        print "result", result
    return result

def document_from_pubmed(record):
    """
    Given a record returned by Entrez for a document in pubmed, pull it apart
    keeping only the data elements useful for VIVO
    """
    d = {}
    d['title'] = record['MedlineCitation']['Article']['ArticleTitle']
    d['date'] = {'month': record['PubmedData']['History'][0]['Month'],
        'day'  : record['PubmedData']['History'][0]['Day'],
        'year' : record['PubmedData']['History'][0]['Year']}
    d['journal'] = record['MedlineCitation']['Article']['Journal']['Title']

    author_list = list(record['MedlineCitation']['Article']['AuthorList'])
    authors = {}
    i = 0
    for author in author_list:
        i = i + 1
        first = author['ForeName']
        if first.find(' ') >= 0:
            first = first[:first.find(' ')]
        last = author['LastName']
        middle = author['Initials']
        if len(middle) == 2:
            middle = str(middle[1])
        else:
            middle = ""
        key = str(i)
        authors[key] = {'first':first, 'middle':middle, 'last':last}
    d['authors'] = authors

    try:
        d['volume'] = record['MedlineCitation']['Article']\
            ['Journal']['JournalIssue']['Volume']
    except:
        pass
    
    try:
        d['issue'] = record['MedlineCitation']['Article']['Journal']\
            ['JournalIssue']['Issue']
    except:
        pass
    d['issn'] = str(record['MedlineCitation']['Article']['Journal']['ISSN'])

    article_id_list = record['PubmedData']['ArticleIdList']
    for article_id in article_id_list:
        attributes = article_id.attributes
        if 'IdType' in attributes:
            if attributes['IdType'] == 'pubmed':
                d['pmid'] = str(article_id)
            elif attributes['IdType'] == 'doi':
                d['doi'] = str(article_id)

    pages = record['MedlineCitation']['Article']['Pagination']['MedlinePgn']
    pages_list = pages.split('-')
    try:
        start = pages_list[0]
        try:
            istart = int(start)
        except:
            istart = -1
    except:
        start = ""
        istart = -1
    try:
        end = pages_list[1]
        if end.find(';') > 0:
            end = end[:end.find(';')]
    except:
        end = ""
    if start != "" and istart > -1 and end != "":
        if int(start) > int(end):
            if int(end) > 99:
                end = str(int(start) - (int(start) % 1000) + int(end))
            elif int(end) > 9:
                end = str(int(start) - (int(start) % 100) + int(end))
            else:
                end = str(int(start) - (int(start) % 10) + int(end))
    d['page_start'] = start
    d['page_end'] = end
    return d

def string_from_document(doc):
    """
    Given a doc structure, create a string representation for printing
    """
    s = ""
    if 'authors' in doc:
        author_list = doc['authors']
        for key in sorted(author_list.keys()):
            value = author_list[key]
            if 'last' not in value or value['last'] is None or \
               value['last'] == "":
                continue
            s = s + value['last']
            if 'first' not in value or value['first'] is None or \
               value['first'] == "":
                s = s + ', '
                continue
            else:
                s = s + ', ' + value['first']
            if 'middle' not in value or value['middle'] is None or \
               value['middle'] == "":
                s = s + ', '
            else:
                s = s + ' ' + value['middle'] + ', '
    if 'title' in doc:
        s = s + '"' + doc['title']+'"'
    if 'journal' in doc:
        s = s + ', ' + doc['journal']
    if 'volume' in doc:
        s = s + ', ' + doc['volume']
    if 'issue' in doc:
        s = s + '(' + doc['issue'] + ')'
    if 'number' in doc:
        s = s + '(' + doc['number'] + ')'
    if 'date' in doc:
        s = s + ', ' + doc['date']['year']
    if 'page_start' in doc:
        s = s + ', pp ' + doc['page_start']
    if 'page_end' in doc:
        s = s + '-' + doc['page_end'] + '.'
    if 'doi' in doc:
        s = s + ' doi: ' + doc['doi']
    if 'pmid' in doc:
        s = s + ' pmid: ' + doc['pmid']
    if 'pmcid' in doc:
        s = s + ' pmcid: ' + doc['pmcid']
    return s

def update_pubmed(pub_uri, doi=None, pmid=None, inVivo=True):
    """
    Given the uri of a pub in VIVO and a module concept dictionary,
    update the PubMed attributes for the paper, and include RDF
    to add to the concept dictionary if necessary
    """
    ardf = ""
    srdf = ""
    if inVivo:

    # Get the paper's attributes from VIVO

        pub = get_publication(pub_uri)
        if 'doi' not in pub and doi is None:
            return ["", ""]
        elif doi is None:
            doi = pub['doi']
        if 'pmid' not in pub:
            pub['pmid'] = None
        if 'pmcid' not in pub:
            pub['pmcid'] = None
        if 'nihmsid' not in pub:
            pub['nihmsid'] = None
        if 'abstract' not in pub:
            pub['abstract'] = None

    else:
        pub = {}
        pub['pmid'] = pmid
        pub['doi'] = doi
        pub['pub_uri'] = pub_uri
        pub['pmcid'] = None
        pub['nihmsid'] = None
        pub['abstract'] = None

    # Get the paper's attributes from PubMed

    try:
        values = get_pubmed_values(doi, pmid)
    except:
        return {}

    if values == {}:
        return ["", ""]

    if 'pmid' not in values:
        values['pmid'] = None
    if 'pmcid' not in values:
        values['pmcid'] = None
    if 'nihmsid' not in values:
        values['nihmsid'] = None
    if 'abstract' not in values:
        values['abstract'] = None

    [add, sub] = update_data_property(pub_uri, "bibo:pmid", pub['pmid'],
                                          values['pmid'])
    ardf = ardf + add
    srdf = srdf + sub

    [add, sub] = update_data_property(pub_uri, "vivo:pmcid", pub['pmcid'],
                                          values['pmcid'])
    ardf = ardf + add
    srdf = srdf + sub

    [add, sub] = update_data_property(pub_uri, "vivo:nihmsid", pub['nihmsid'],
                                          values['nihmsid'])
    ardf = ardf + add
    srdf = srdf + sub

    [add, sub] = update_data_property(pub_uri, "bibo:abstract", pub['abstract'],
                                          values['abstract'])
    ardf = ardf + add
    srdf = srdf + sub

    # Process the keyword_list and link to concepts in VIVO. If the
    # concept is not in VIVO, add it

    if 'keyword_list' in values:
        for keyword in values['keyword_list']:
            if keyword in concept_dictionary:
                keyword_uri = concept_dictionary[keyword]
                [add, sub] = update_resource_property(pub_uri, \
                    "vivo:hasSubjectArea", None, keyword_uri)
                ardf = ardf + add
                srdf = srdf + sub
            else:
                [add, keyword_uri] = make_concept_rdf(keyword)
                ardf = ardf + add
                concept_dictionary[keyword] = keyword_uri
                [add, sub] = update_resource_property(pub_uri, \
                    "vivo:hasSubjectArea", None, keyword_uri)
                ardf = ardf + add
                srdf = srdf + sub

    # Process the grants cited lists -- VIVO and PubMed

    if 'grants_cited' in values:
        pubmed_grants_cited = values['grants_cited']
    else:
        pubmed_grants_cited = None

    if 'grants_cited' in pub:
        if pubmed_grants_cited is None:    # Remove grants cited from VIVO
            for grant in pub['grants_cited']:
                [add, sub] = update_data_property(pub_uri, 'ufVivo:grantCited',
                                                    grant, None)
                ardf = ardf + add
                srdf = srdf + sub
        else:                                # Compare lists
            for grant in pub['grants_cited']:
                if grant not in pubmed_grants_cited:
                    [add, sub] = update_data_property(pub_uri, \
                        'ufVivo:grantCited', grant, None) # remove from VIVO
                    ardf = ardf + add
                    srdf = srdf + sub
            for grant in pubmed_grants_cited:
                if grant not in pub['grants_cited']:
                    [add, sub] = update_data_property(pub_uri, \
                        'ufVivo:grantCited', None, grant) # add to VIVO
                    ardf = ardf + add
                    srdf = srdf + sub
    else:
        if pubmed_grants_cited is None:    # No grants cited
            pass
        else:                                # Add Pubmed grants cited to VIVO
            for grant in pubmed_grants_cited:
                [add, sub] = update_data_property(pub_uri, 'ufVivo:grantCited',
                                                    None, grant)
                ardf = ardf + add
                srdf = srdf + sub

    #  Web page for full text

    if 'full_text_uri' in pub and 'full_text_uri' in values:
        # both have URI
        if pub['full_text_uri'] == values['full_text_uri']:
            pass # both have same URI for full text, nothing to do
        else:
            sub = remove_uri(pub['webpage']['webpage_uri'])
            srdf = srdf + sub

    elif 'full_text_uri' in pub and 'full_text_uri' not in values:
        pass  # keep the VIVO full text URI, might not be PubMed Central

    elif 'full_text_uri' not in pub and 'full_text_uri' in values:

        # Add web page

        [add, webpage_uri] = \
            make_webpage_rdf(values['full_text_uri'])
        ardf = ardf + add

        # Point the pub at the web page

        [add, sub] = update_resource_property(pub_uri, 'vivo:webpage', None,
            webpage_uri)
        ardf = ardf + add
        srdf = srdf + sub

        # Point the web page at the pub

        [add, sub] = update_resource_property(webpage_uri, 'vivo:webpageOf',
            None, pub_uri)
        ardf = ardf + add
        srdf = srdf + sub

    else:
        pass # Full text URI is not in VIVO and not in PubMed

    return [ardf, srdf]
