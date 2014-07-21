"""
    test_vivo_sparql_query.py -- issue a SPARQL query to VIVO and return
    the result as a JSON object

    Version 0.1 MC 2013-12-28
    --  Initial version.
    Version 0.2 MC 2014-07-21
    --  Upgraded for vivotools 2.0

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"

from vivofoundation import vivo_sparql_query
import json
from datetime import datetime

print datetime.now(), "Start"

query = """
    SELECT ?p ?o
    WHERE {
      <http://vivo.ufl.edu/individual/n3715> ?p ?o
    }
    ORDER BY ?p
    """

data = vivo_sparql_query(query, debug=True) # show the encoded query                                # issue the query, return the data
print "Retrieved data:\n" + json.dumps(data, sort_keys=True, indent=4)
print "Items found = ", len(data["results"]["bindings"])
print datetime.now(), "Finish"
