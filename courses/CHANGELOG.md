    Addition RDF is created.  No subtraction RDF is created.

    Version 0.0 MC 2013-08-03
    --  Read OUR data and UFID person data from VIVO. Create the process frame,
        throw and catch exceptions
    Version 0.1 MC 2013-10-03
    --  Remove redundant bi-directional assertions.  These will be added by
        the inferencer
    --  Write a position-data file for all people to be added
    --  Took out references to sub file
    --  Passed XML validator
    Version 0.2 MC 2013-10-10
    --  Correct ontology errors in roles, Course and Course section
    --  remove functions to make reverse assertions that will be handled by
        inferencer
    Version 0.3 MC 2013-10-19
    --  Added UFEntity to course and section to support distinguishing from
        courses and sections people may have taught outside UF
    --  Moved CourseRole creation to make_section.  All linkages between
        entities are added at the section level.
    --  Show vivotools version
    Version 0.4 MC 2013-12-15
    --  escape the course title to prevent RDF ingest errors
    Version 0.5 MC 2014-06-23
    --  Handle unicode using standard vivotools approach.
    --  Use codecs to write XML.
    --  Add labels to the TeacherRole for courses -- this is a
        workaround required by the VIVO interface.
    --  Fix bug regarding TeacherRoles for courses -- these must be
        singular, not one per section.
    --  Fix version number in RDF
    --  Improve code formatting
    --  Clean up print destinations
    --  Runs with current vivotools

    Future enhancements:
     -- Handle instructor new to existing section (team teaching).

