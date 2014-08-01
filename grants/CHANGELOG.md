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
