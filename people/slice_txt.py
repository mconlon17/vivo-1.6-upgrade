#!/usr/bin/env/python

"""
    slice_txt.py: Given a txt file, select records
    Version 0.1 MC 2014-07-19
     -- framework

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from datetime import datetime

#   Start here

print datetime.now(), "Start"

in_file = open('position_data.csv','r')
out_file = open('small_position_data.txt','w')
k = 0

for line in in_file:
    k = k + 1
    if k % 10000 == 0:
        print k
    if line[9] == '8':
        print >>out_file, line,
in_file.close()
out_file.close()

print datetime.now(), "End"
