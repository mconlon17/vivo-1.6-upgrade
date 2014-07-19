h1. Running Person Ingest

1)  Using a SSH client connect to vivostagingweb.vivo.ufl.edu

2)  In your home directory (or directory of your choosing) run the following
<pre>
git clone git@ctsit-forge.ctsi.ufl.edu:vivo-people-ingest.git</pre>
3) CD into the project

4) Start a screen using 
<pre>
screen -S ingest
</pre>
5) Screen will start and the session will be named ingest, this will be important since you may drop connection to the server while the ingest is running

6) All the necessary files will be in the repo and the next step is to simply run the ingest by
<pre> ./run-me-ingest.sh</pre>

7) If there are any missing libraries of python, install them using below instructions, else proceed to step 8
<pre> sudo easy_install <library_name></pre>
example : <pre> sudo easy_install tempita
 sudo easy_install python-dateutil</pre>
The libraries should be installed in the site-packages under _"/Library/Python/2.7/site-packages"_

8) It will ask you  to delete the old output files from the previous run, hit 'y' for the 4/5 files

9) The ingest is now running

10) Detach from the screen using control-A then D

11) To reattach and periodically check the progress type 
<pre> screen -r ingest </pre>

12) After the ingest is run do a git status and there should be 4/5 files to upload
* contact_data.pcl
* people_add.rdf
* people_sub.rdf
* person-ingest.log
* privacy_data.pci

13) Upload the output files to the repo 

14) Pull the files onto your local machine so that you can access them

15) Go to vivo.ufl.edu and login

16) Go to Site Admin and Add/Remove RDF data

17) Select Add instance data, and that RDF/XML is selected from the drop down menu

18) Click choose file and select the people_add.rdf and click submit

19) Wait for the browser to time out, this may or not signal the end of the add. Open the people_add.rdf and look for a change near the end of the file and check this against the site to see if the change is reflected. If everything looks good you can continue with the sub.

20) Select the Remove Mixed RDF radio button and choose the people_sub.rdf file and click submit. This should take substantially less time. Again check for a change near the end of the sub file and compare it to the site. If everything checks out the ingest for the week is complete.

h2.ADDENDUM

contact_data.csv
It is pipe '|' delimited and contains headers. Contains about 2 Million rows 
The following information is stored on the CTSI-SRVTASK11 server in the VIVO_DATA.dbo.VIVO_PERSON_INGEST
UFID - nvarchar
FIRST_NAME - nvarchar
LAST_NAME - nvarchar
MIDDLE_NAME - nvarchar
NAME_PREFIX - nvarchar
NAME_SUFFIX - nvarchar
DISPLAY_NAME - nvarchar
GATORLINK - nvarchar
JOBTITLE - nvarhcar
LONGTITLE - nvarchar
UF_BUSINESS_EMAIL - nvarchar
UF_BUSINESS_PHONE - nvarchar
UF_BUSINESS_FAX - nvarchar
WORKINGTITLE - nvarchar

The contact_data.csv file contains the following:
UFID
FIRST_NAME
LAST_NAME
MIDDLE_NAME
NAME_PREFIX
NAME_SUFFIX
DISPLAY_NAME
GATORLINK
WORKINGTITLE
UF_BUSINESS_EMAIL
UF_BUSINESS_PHONE
UF_BUSINESS_FAX



------------------------------------------

privacy_data.csv
It is pipe '|' delimited and contains headers. Contains about 2 Million rows 
The following information is stored on the CTSI-SRVTASK11 server in the VIVO_DATA.dbo.tbl_privacy_dump
UFID - varchar
UF_SECURITY_FLG - varchar
UF_PROTECT_FLG - varchar
UF_PUBLISH_FLG - varchar

The privacy_data.csv contains the following:
UFID
UF_SECURITY_FLG
UF_PROTECT_FLG
UF_PUBLISH_FLG

-------------------------------------------

position_data.csv
It is pipe '|' delimited and contains headers. Contains about 41k rows

The following information is stored on the CTSI-SRVTASK11 server in the VIVO_DATA.dbo.tbl_hr_data
DEPTID - varchar
UFID - varchar
JOBCODE - varchar
START_DATE - date
END_DATE - date
JOBCODE_DESCRIPTION -  varchar
SAL_ADMIN_PLAN - varchar

The position_data.csv contains the following:
DEPTID
UFID
JOBCODE - No leading 0's
START_DATE
END_DATE
JOBCODE_DESCRIPTION
SAL_ADMIN_PLAN


You need to delete the following files before each run of the person-ingest.py

Delete all the pcl files
*.pcl 
Delete all the people_ files

people_add.rdf
people_exc.lst
people_sub.rdf

ok...