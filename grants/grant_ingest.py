#!/usr/bin/env/python

"""
    grant-ingest.py: Given grant data from the Division of Sponsored Programs,
    compare to VIVO.  Comparison is made on peoplesoft contract number (pcn)
    Then create addition and subtraction RDF for VIVO to manage
    the following entities:

    grants -- add and update.  Will create sub-awards as grants if needed
    funding org -- update only.  Grant ingest does not create funding orgs
    people (PI, Co-I, Key Personnel) -- update only.  Grant ingest does not
        create people
    connecting roles -- add
    administering org -- update only.  Grant ingest does not create UF orgs.

    There are three cases:

    Case 1: The grant is in DSP, but not in VIVO.  The grant will be added.
    Case 2: The grant is in VIVO, but not in DSP.  The grant will be untouched.
    Case 3: The grant is in both DSP and VIVO.  The grant will be updated.

    To Do
    --  update for VIVO-ISF
    --  use vivofoundation and vivogrants
    --  use a prepare function
    
    Future
    --  Make person_add file for people not found
    --  Add -v parameter to command line to route log to stdout
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.8"

from datetime import datetime
import random # for testing purposes, select subsets of records to process
import tempita
import sys
import os
import vivotools as vt
import codecs

def make_dsp_dictionary(file_name="grant_data.csv", debug=False):
    """
    Read a CSV file with grant data from the Division of Sponsored Programs.
    Create a dictionary with one entry per PeopleSoft Contract Number (pcn).

    If multiple rows exist in the data for a particular pcn,
    the last row will be used in the dictionary
    """
    dsp_dictionary = {}
    ardf = ""
    error_count = 0
    dsp_data = vt.read_csv(file_name)
    for row in dsp_data.keys():
        any_error = False

        if row % 100 == 0:
            print row
            
        pcn = dsp_data[row]['AwardID']

        # Simple attributes

        dsp_data[row]['pcn'] = pcn
        dsp_data[row]['title'] = improve_grant_title(dsp_data[row]['Title'])
        dsp_data[row]['sponsor_award_id'] = dsp_data[row]['SponsorAwardID']
        dsp_data[row]['local_award_id'] = dsp_data[row]['AwardID']
        dsp_data[row]['harvested_by'] = 'Python Grants ' + __version__
        dsp_data[row]['date_harvested'] = str(datetime.now())

        # Award amounts

        try:
            total = float(dsp_data[row]['TotalAwarded'])
            dsp_data[row]['total_award_amount'] = dsp_data[row]['TotalAwarded']
        except ValueError:
            total = None
            print >>exc_file, pcn, "Total Award Amount", \
                dsp_data[row]['TotalAwarded'], "invalid number"
            any_error = True

        try:
            direct = float(dsp_data[row]['DirectCosts'])
            dsp_data[row]['grant_direct_costs'] = dsp_data[row]['DirectCosts']
        except ValueError:
            direct = None
            print >>exc_file, pcn, "Grant Direct Costs", \
                dsp_data[row]['DirectCosts'], "invalid number"
            any_error = True

        if total is not None and total < 0:
            print >>exc_file, pcn, "Total Award Amount", \
                dsp_data[row]['total_award_amount'], "must not be negative"
            any_error = True

        if direct is not None and direct < 0:
            print >>exc_file, pcn, "Grant Direct Costs", \
                dsp_data[row]['grant_direct_costs'], "must not be negative"
            any_error = True

        if direct is not None and total is not None and total < direct:
            print >>exc_file, pcn, "Total Award Amount", \
                dsp_data[row]['total_award_amount'],\
                "must not be less than Grant Direct Costs", \
                dsp_data[row]['grant_direct_costs']
            any_error = True

        # Admin department

        [found, administered_by_uri] = vt.find_deptid(dsp_data[row]['DeptID'], \
            deptid_dictionary)
        if found:
            dsp_data[row]['administered_by_uri'] = administered_by_uri
        else:
            print >>exc_file, pcn, "DeptID", dsp_data[row]['DeptID'], \
                "not found in VIVO"
            any_error = True

        # Sponsor

        [found, sponsor_uri] = find_sponsor(dsp_data[row]['SponsorID'], \
            sponsor_dictionary)
        if found:
            dsp_data[row]['sponsor_uri'] = sponsor_uri
        else:
            print >>exc_file, pcn, "Sponsor", dsp_data[row]['SponsorID'], \
                "not found in VIVO"
            any_error = True

        # Start and End dates

        try:
            start_date = datetime.strptime(dsp_data[row]['StartDate'],\
                '%m/%d/%Y')
            if start_date in date_dictionary:
                start_date_uri = date_dictionary[start_date]
            else:
                [add, start_date_uri] = \
                    vt.make_datetime_rdf(start_date.isoformat())
                date_dictionary[start_date] = start_date_uri
                ardf = ardf + add
        except ValueError:
            print >>exc_file, pcn, "Start date", dsp_data[row]['StartDate'], \
                "invalid"
            start_date = None
            start_date_uri = None
            any_error = True

        try:
            end_date = datetime.strptime(dsp_data[row]['EndDate'],\
                '%m/%d/%Y')
            if end_date in date_dictionary:
                end_date_uri = date_dictionary[end_date]
            else:
                [add, end_date_uri] = \
                    vt.make_datetime_rdf(end_date.isoformat())
                date_dictionary[end_date] = end_date_uri
                ardf = ardf + add
        except ValueError:
            print >>exc_file, pcn, "End date", dsp_data[row]['EndDate'], \
                "invalid"
            end_date = None
            end_date_uri = None
            any_error = True


        if end_date is not None and start_date is not None and \
            end_date < start_date:
            print >>exc_file, pcn, "End date", dsp_data[row]['EndDate'], \
                "before start date", dsp_data[row]['StartDate']
            any_error = True

        [found, dti_uri] = find_datetime_interval(start_date_uri, \
            end_date_uri, datetime_interval_dictionary)
        if found:
            dsp_data[row]['dti_uri'] = dti_uri
        else:
            if start_date_uri is not None or end_date_uri is not None:
                [add, dti_uri] = vt.make_dt_interval_rdf(start_date_uri, \
                    end_date_uri)
                datetime_interval_dictionary[start_date_uri+\
                    end_date_uri] = dti_uri
                ardf = ardf + add
                dsp_data[row]['dti_uri'] = dti_uri

        # Investigators

        investigator_names = [['pi_uris', 'PI'], ['coi_uris', 'CoPI'],\
            ['inv_uris', 'Inv']]
        for uri_type, ufid_type in investigator_names:
            dsp_data[row][uri_type] = []
            if dsp_data[row][ufid_type] != '' and \
                dsp_data[row][ufid_type] != None:
                ufid_list = dsp_data[row][ufid_type].split(',')
                for ufid in ufid_list:
                    [found, uri] = vt.find_person(ufid, ufid_dictionary)
                    if found:
                        dsp_data[row][uri_type].append(uri)
                    else:
                        print >>exc_file, pcn, ufid_type, ufid, \
                            "not found in VIVO"
                        any_error = True

        # If there are any errors in the data, we can't add the grant

        if any_error:
            error_count = error_count + 1
            continue

        # Assign row to dictionary entry

        dsp_dictionary[pcn] = dsp_data[row]
    return [ardf, error_count, dsp_dictionary]

# Driver program starts here

debug = False

# Fraction of records to be processed. Set to 1.0 to process all

sample = 1.00

if len(sys.argv) > 1:
    dsp_file_name = str(sys.argv[1])
else:
    dsp_file_name = "vivo_grants.txt"
file_name, file_extension = os.path.splitext(dsp_file_name)

add_file = codecs.open(file_name+"_add.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
sub_file = codecs.open(file_name+"_sub.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
log_file = codecs.open(file_name+"_log.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
exc_file = codecs.open(file_name+"_exc.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')

print >>log_file, datetime.now(), "Grant Ingest Version", __version__
print >>log_file, datetime.now(), "VIVO Tools Version", vt.__version__

add_file.write(vt.rdf_header())
sub_file.write(vt.rdf_header())

print >>log_file, datetime.now(), "Make VIVO DeptID Dictionary"
deptid_dictionary = vt.make_deptid_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO deptid dictionary has ", \
    len(deptid_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO UFID Dictionary"
ufid_dictionary = vt.make_ufid_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO ufid dictionary has ", \
    len(ufid_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO Sponsor Dictionary"
sponsor_dictionary = make_sponsor_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO sponsor dictionary has ", \
    len(sponsor_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO Date Dictionary"
date_dictionary = \
    make_date_dictionary(datetime_precision="vivo:yearMonthDayPrecision",\
    debug=debug)
print >>log_file, datetime.now(), "VIVO date dictionary has ", \
    len(date_dictionary), " entries"

print >>log_file, datetime.now(), "Make VIVO Datetime Interval Dictionary"
datetime_interval_dictionary = make_datetime_interval_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO datetime interval dictionary has ", \
    len(datetime_interval_dictionary), " entries"


print >>log_file, datetime.now(), "Make VIVO Grant Dictionary"
grant_dictionary = make_grant_dictionary(debug=debug)
print >>log_file, datetime.now(), "VIVO grant dictionary has ", \
    len(grant_dictionary), " entries"

#   Read the DSP data and make a dictionary ready to be processed.  The
#   dictionary will contain data values and references to VIVO entities
#   (people and dates) sufficient to create or update each grant.  New dates
#   and datetime intervals might be needed.  The make_dsp_dictionary process
#   creates these and returns RDF for them to be added to VIVO.

print >>log_file, datetime.now(), "Read DSP Grant Data from", \
      dsp_file_name
[ardf, error_count, dsp_dictionary] = \
    make_dsp_dictionary(file_name=dsp_file_name,\
    debug=debug)
if ardf != "":
    add_file.write(ardf)
print >>log_file, datetime.now(), "DSP data has ", len(dsp_dictionary), \
    " valid entries"
print >>log_file, datetime.now(), "DSP data has ", error_count, \
    " invalid entries.  See exception file for details"

#   Loop through the DSP data and the VIVO data, adding each pcn to the
#   action report.  1 for DSP only.  2 for VIVO only.  3 for both

action_report = {}
for pcn in dsp_dictionary.keys():
    action_report[pcn] = action_report.get(pcn, 0) + 1
for pcn in grant_dictionary.keys():
    action_report[pcn] = action_report.get(pcn, 0) + 2

print >>log_file, datetime.now(), "Action report has ", len(action_report), \
    "entries"

#   Loop through the action report for each pcn.  Count and log the cases

n1 = 0
n2 = 0
n3 = 0
for pcn in action_report.keys():
    if action_report[pcn] == 1:
        n1 = n1 + 1
    elif action_report[pcn] == 2:
        n2 = n2 + 1
    else:
        n3 = n3 + 1

print >>log_file, datetime.now(), n1,\
    " Grants in DSP only.  These will be added to VIVO."
print >>log_file, datetime.now(), n2,\
    " Grants in VIVO only.  No action will be taken."
print >>log_file, datetime.now(), n3,\
    " Grants in both DSP and VIVO.  Will be updated as needed."

# Set up complete.  Now loop through the action report. Process each pcn

print >>log_file, datetime.now(), "Begin Processing"
row = 0
for pcn in sorted(action_report.keys()):
    row = row + 1
    if row % 100 == 0:
        print row

    ardf = ""
    srdf = ""
    r = random.random()  # random floating point between 0.0 and 1.0
    if r > sample:
        continue

    if action_report[pcn] == 1:

        #   Case 1: DSP Only. Add Grant to VIVO.

        print >>log_file, datetime.now(), pcn, "Case 1: Add   "

        grant_data = dsp_dictionary[pcn]
        [add, grant_uri] = add_grant(grant_data)
        ardf = ardf + add

    elif action_report[pcn] == 2:

        # Case 2: VIVO Only.  Nothing to do.

        pass

    else:

        #   Case 3: DSP and VIVO. Update grant.

        print >>log_file, datetime.now(), pcn, "Case 3: Update"

        grant_uri = grant_dictionary[pcn]
        grant_data = dsp_dictionary[pcn]

        [add, sub] = update_grant(grant_uri, grant_data)
        ardf = ardf + add
        srdf = srdf + sub

    if ardf != "":
        add_file.write(ardf)
    if srdf != "":
        sub_file.write(srdf)

#   Done processing the Grants.  Wrap-up

add_file.write(vt.rdf_footer())
sub_file.write(vt.rdf_footer())
print >>log_file, datetime.now(), "End Processing"

add_file.close()
sub_file.close()
log_file.close()
exc_file.close()
