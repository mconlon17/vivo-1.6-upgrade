#!/usr/bin/env/python

"""
    update_privacy.py: Given privacy data in a txt file, create
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
