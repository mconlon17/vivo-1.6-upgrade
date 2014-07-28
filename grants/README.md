# Grant ingest

Getting started with grant ingest.

## Innovations

* Adding a grant is just a call to create a URI that assigns type grant.  Then update 
that URI.  So all attributes for all grants are handled as updates.
* All dates are attempted to be reused.  Dates and datetime intervals are only 
created if they can not be found in VIVO
* The source data is read into a dictionary and extensively prepped for processing.  
Hopefully this clarifies and simplifies the eventual processing.  Also gathers
all the error checking, corrections and exception processing in one place.
* Personnel on grants are classified into three types: 1) PIs -- any number of people 
can be PI; 2) Co-PI -- any number can be co-PI, and 3) Investigator -- any number 
of people can be investigators

## Notes

Takes about three minutes for dictionary loading

## Production Process

-   Ed Neu runs process to create vivo_grants.txt
-   Ed Neu SFTP's file to Shands FTP site using CTS-VIVO with password 
-   Script to do the following:
    -   Delete old output files named vivo_grants_add.rdf and vivo_grants_sub.rdf
    -   Delete old log files named vivo_grants_log.txt and vivo_grants_exc.txt
    -   Delete old input file named vivo_grants.txt
    -   Run the following commands:
        -   lftp sftp://cts-vivo:password@sftp.ahc.ufl.edu -e "get vivo_grants.txt; bye"
        -   python grant_ingest.py
-   Through site admin interface, run add on vivo_grants_add.rdf
-   Through site admin interface, run sub on vivo_grants_sub.rdf
