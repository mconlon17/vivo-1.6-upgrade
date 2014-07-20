#!/usr/bin/env/python

"""
    update_contact.py: Given contact data in a txt file, create
    a shelve object
    
    Version 0.1 MC 2014-07-19
     -- first version

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from datetime import datetime
from vivofoundation import read_csv
import shelve
import os

#   Start here

print datetime.now(), "Start"
contact_data = read_csv('contact_data.txt')
try:
    os.remove('contact')
except:
    pass
contact =shelve.open('contact')
k = 0
for row,val in contact_data.items():
    k = k + 1
    if k % 1000 == 0:
        print k
    contact[str(val['UFID'])] = val
contact.close()

# Deptid_exceptions

deptid_exceptions_data = read_csv('deptid_exceptions_data.txt')
try:
    os.remove('deptid_exceptions')
except:
    pass
deptid_exceptions =shelve.open('deptid_exceptions')
k = 0
for row,val in deptid_exceptions_data.items():
    k = k + 1
    if k % 1000 == 0:
        print k
    deptid_exceptions[str(val['deptid_pattern'])] = val
deptid_exceptions.close()

# Privacy

privacy_data = read_csv('privacy_data.txt')
try:
    os.remove('privacy')
except:
    pass
privacy =shelve.open('privacy')
k = 0
for row,val in privacy_data.items():
    k = k + 1
    if k % 1000 == 0:
        print k
    privacy[str(val['UFID'])] = val
privacy.close()

print datetime.now(), "End"
