#!/usr/bin/env/python

"""
    test_fix_email.py: Given an email string, try to fix it
    Version 0.0 MC 2014-02-24
     -- framework

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.0"

from datetime import datetime
import re

def fix_email(email, exp = re.compile(r'\w+\.*\w+@\w+\.(\w+\.*)*\w+')):
    """
    Given an email string, fix it
    """
    s = exp.search(email)
    if s is None:
        return ""
    elif s.group() is not None:
        return s.group()
    else:
        return ""

#   Start here

print datetime.now(), "Start"

email = "mconlon@ufl.edu"
print email, "\t", ':' + fix_email(email) + ':'

email = "mtelonis@zoo.ufl.edu<br />"
print email, "\t", ':' + fix_email(email) + ':'

email = "m.conlon@ufl.edu"
print email, "\t", ':' + fix_email(email) + ':'

email = "mike.conlon@ufl.edu"
print email, "\t", ':' + fix_email(email) + ':'

email = " m.conlon@ufl.edu "
print email, "\t", ':' + fix_email(email) + ':'

email = " m.conlon@stat.ufl.edu "
print email, "\t", ':' + fix_email(email) + ':'


email = " m.conlon@stat.ufl..edu "
print email, "\t", ':' + fix_email(email) + ':'


email = " m.conlon@stat.ufl.edu.uk "
print email, "\t", ':' + fix_email(email) + ':'

email = " mconlon@/ufl.edu "
print email, "\t", ':' + fix_email(email) + ':'

print datetime.now(), "End"
