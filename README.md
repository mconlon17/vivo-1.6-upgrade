# VIVO 1.6 Upgrade On Hold

*After consideration of the effort required for UF to upgrade to VIVO 1.6, the demands 
on the UF VIVO support team for additional data, data quality and data products, and
the possibility of implementing an enterprise solution to manage the data currently
aggregated in VIVO, we have decided to delay the VIVO 1.6 upgrade indefinitely.  We
remain fully committed to VIVO and to the assembly and maintenance of the scholarly
record of the University of Florida.  We do not feel it is in the best interests of the university to 
upgrade at this time.*

We had hoped to take advantage of the bi-directional API feature of VIVO 1.7 to develop
tools for managing and displaying VIVO data.  We will develop tools for 1.5, but these will
be limited to display tools only.

We will upgrade all our ingests and vivotools for 1.5 to improve the functioning of
the ingests, document their functions, improve separation of enterprise data
cleaning, abstract representation, and output to a specific ontology.  This effort will
improve operations and prepare us for future implementation of an enterprise system, 
VIVO 1.7 or both.  We will migrate the VIVO hosting from AWS to CNS to lower cost of
operation.

---

Software for upgrading UF VIVO from 1.5.2 to 1.6.3.  Core ingests and tools upgrades.

To be upgraded:

1. Person Ingest
1. Papers Ingest
1. Grants Ingest
1. Course Ingest
1. UF VIVO ontology extensions
1. VIVO Tools

Additional utilities and SPARQL queries will be needed.  Everything will be in this repo.

# Basic approach

1.  Use a VIVO 1.6.3 vagrant to develop ingests for test cases.  All development and testing done off-line.  All software, documentation and other
artifacts will be posted to this repo.
1.  In parallel, use the vagrant to deploy a new 1.6.3 staging instance and a new 1.6.3 production instance at UF.  These
insances will eventually replace the 1.5.2 instances currently hosted at Amazon. 
1.  Upgrade the UF VIVO database on the new staging instance to 1.6.3
1.  Address the ontology extensions in the updated database.  Insure proper conversion of data, and operation of extensions.
1.  Use new ingests in staging.
1.  Once all ingests are tested and approved in staging, copy staging to production and run ingests in production and verify results.
1.  Once ingests are operational in production, swap the VIVO URL vivo.ufl.edu from pointing at the 1.5.2 release at Amazon to
point at the 1.6.3 release at UF.
1.  Retire the 1.5.2 instances at Amazon.