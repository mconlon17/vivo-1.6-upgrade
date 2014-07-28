# Course Ingest

## Creating Terms

Academic Terms must be in VIVO before course ingest is run. We typically load an entire year at a time, so three terms must be created before course ingest is run.  Follow the steps below:

1. Navigate to the Ontology Class Control Panel for DateTimeInterval
1. Select Add a New Individual of This Class
1. Enter the Label in the resulting field.  At UF the label will be "Summer" "Spring" or "Fall" followed by a space followed by the 4 digit year.  Example: "Summer 1997"
1.Select Create New
1. Select Edit Individual
1. Click on Add Type
1. Select Academic Term

## Backing out an Update


To back out an update: Add the sub.rdf -> Sub the add.rdf 


Data comes from the UF_STUDENT_WAREHOUSE

Course Ingest is run once a semester to catch up past semesters
 


## Course ingest process


 
1.
Run course ingest -> produce course_pos.csv "6000" of new people not in VIVO 

2.
Concat position_data.csv course_pos.csv -> position_data.csv (1 header, position data, course data) (>>) Line both files individually then the cat'd file 

3.
Run person_ingest as ususal (all steps) 
1.
Should contain adds for the ~600 new people 


4.
Run course ingest again -> produce an EMPTY courses_pos.csv  
1.
Non-empty stop and discuss 


5.
Empty course_pos.csv -> upload add.rdf to vivo 

