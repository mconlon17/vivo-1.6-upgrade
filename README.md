# VIVO 1.6 Upgrade

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