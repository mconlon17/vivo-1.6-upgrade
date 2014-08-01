#!/usr/bin/env/python
""" vivopubs.py -- A library of useful things for working with VIVO pubs

    See CHANGELOG for a running account of the changes to vivopubs
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "2.00"


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
