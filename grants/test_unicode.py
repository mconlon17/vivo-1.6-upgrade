#!/usr/bin/env/python

"""
    test_unicode.py: Read test data with non-ascii.  Write it to an
    XML file with encoding
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from datetime import datetime
from vivotools import read_csv
import random # for testing purposes, select subsets of records to process
import tempita
import sys
import os
import vivotools as vt
import codecs
import csv
import string

def improve_grant_title(s):
    """
    DSP uses a series of abbreviations to fit grant titles into limited text
    strings.  Funding agencies often restrict the length of grant titles and
    faculty often clip their titles to fit in available space.  Here we reverse
    the process and lengthen the name for readability
    """
    if s == "":
        return s
    if s[len(s)-1] == ',':
        s = s[0:len(s)-1]
    if s[len(s)-1] == ',':
        s = s[0:len(s)-1]
    s = s.lower() # convert to lower
    s = s.title() # uppercase each word
    s = s + ' '   # add a trailing space so we can find these abbreviated
                  # words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @") # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace(",", " !") # might be two commas in input
    t = t.replace("-", " #")
    t = t.replace("'S ", "'s ")
    t = t.replace("2-blnd ", "Double-blind ")
    t = t.replace("2blnd ", "Double-blind ")
    t = t.replace("A ", "a ")
    t = t.replace("Aav ", "AAV ")
    t = t.replace("Aca ", "Academic ")
    t = t.replace("Acad ", "Academic ")
    t = t.replace("Acp ", "ACP ")
    t = t.replace("Acs ", "ACS ")
    t = t.replace("Act ", "Acting ")
    t = t.replace("Adj ", "Adjunct ")
    t = t.replace("Adm ", "Administrator ")
    t = t.replace("Admin ", "Administrative ")
    t = t.replace("Adv ", "Advisory ")
    t = t.replace("Advanc ", "Advanced ")
    t = t.replace("Aff ", "Affiliate ")
    t = t.replace("Affl ", "Affiliate ")
    t = t.replace("Ahec ", "AHEC ")
    t = t.replace("Aldh ", "ALDH ")
    t = t.replace("Alk1 ", "ALK1 ")
    t = t.replace("Alumn Aff ", "Alumni Affairs ")
    t = t.replace("Amd3100 ", "AMD3100 ")
    t = t.replace("Aso ", "Associate ")
    t = t.replace("Asoc ", "Associate ")
    t = t.replace("Assoc ", "Associate ")
    t = t.replace("Ast ", "Assistant ")
    t = t.replace("Ast #G ", "Grading Assistant ")
    t = t.replace("Ast #R ", "Research Assistant ")
    t = t.replace("Ast #T ", "Teaching Assistant ")
    t = t.replace("Bpm ", "BPM ")
    t = t.replace("Brcc ", "BRCC ")
    t = t.replace("Cfo ", "Chief Financial Officer ")
    t = t.replace("Cio ", "Chief Information Officer ")
    t = t.replace("Clin ", "Clinical ")
    t = t.replace("Cms ", "CMS ")
    t = t.replace("Cns ", "CNS ")
    t = t.replace("Co ", "Courtesy ")
    t = t.replace("Cog ", "COG ")
    t = t.replace("Communic ", "Communications ")
    t = t.replace("Compar ", "Compare ")
    t = t.replace("Coo ", "Chief Operating Officer ")
    t = t.replace("Copd ", "COPD ")
    t = t.replace("Cpb ", "CPB ")
    t = t.replace("Crd ", "Coordinator ")
    t = t.replace("Ctr ", "Center ")
    t = t.replace("Cty ", "County ")
    t = t.replace("Dbl-bl ", "Double-blind ")
    t = t.replace("Dbl-blnd ", "Double-blind ")
    t = t.replace("Dbs ", "DBS ")
    t = t.replace("Dev ", "Development ")
    t = t.replace("Devel ", "Development ")
    t = t.replace("Dist ", "Distinguished ")
    t = t.replace("Dna ", "DNA ")
    t = t.replace("Doh ", "DOH ")
    t = t.replace("Doh/cms ", "DOH/CMS ")
    t = t.replace("Double Blinded ", "Double-blind ")
    t = t.replace("Double-blinded ", "Double-blind ")
    t = t.replace("Dpt-1 ", "DPT-1 ")
    t = t.replace("Dtra0001 ", "DTRA0001 ")
    t = t.replace("Dtra0016 ", "DTRA-0016 ")
    t = t.replace("Educ ", "Education ")
    t = t.replace("Eff/saf ", "Safety and Efficacy ")
    t = t.replace("Emer ", "Emeritus ")
    t = t.replace("Emin ", "Eminent ")
    t = t.replace("Enforce ", "Enforcement ")
    t = t.replace("Eng ", "Engineer ")
    t = t.replace("Environ ", "Environmental ")
    t = t.replace("Epr ", "EPR ")
    t = t.replace("Eval ", "Evaluation ")
    t = t.replace("Ext ", "Extension ")
    t = t.replace("Fdot ", "FDOT ")
    t = t.replace("Fdots ", "FDOT ")
    t = t.replace("Fhtcc ", "FHTCC ")
    t = t.replace("Finan ", "Financial ")
    t = t.replace("Fla ", "Florida ")
    t = t.replace("For ", "for ")
    t = t.replace("G-csf ", "G-CSF ")
    t = t.replace("Gen ", "General ")
    t = t.replace("Gis ", "GIS ")
    t = t.replace("Gm-csf ", "GM-CSF ")
    t = t.replace("Grad ", "Graduate ")
    t = t.replace("Hcv ", "HCV ")
    t = t.replace("Hiv ", "HIV ")
    t = t.replace("Hiv-infected ", "HIV-infected ")
    t = t.replace("Hiv/aids ", "HIV/AIDS ")
    t = t.replace("Hlb ", "HLB ")
    t = t.replace("Hlth ", "Health ")
    t = t.replace("Hou ", "Housing ")
    t = t.replace("Hsv-1 ", "HSV-1 ")
    t = t.replace("I/ii ", "I/II ")
    t = t.replace("I/ucrc ", "I/UCRC ")
    t = t.replace("Ica ", "ICA ")    
    t = t.replace("Icd ", "ICD ")
    t = t.replace("Ieee ", "IEEE ")
    t = t.replace("Ifas ", "IFAS ")
    t = t.replace("Igf-1 ", "IGF-1 ")
    t = t.replace("Ii ", "II ")
    t = t.replace("Ii/iii ", "II/III ")
    t = t.replace("Iii ", "III ")
    t = t.replace("In ", "in ")
    t = t.replace("Info ", "Information ")
    t = t.replace("Inter-vention ", "Intervention ")
    t = t.replace("Ipa ", "IPA ")
    t = t.replace("Ipm ", "IPM ")
    t = t.replace("Ippd ", "IPPD ")
    t = t.replace("Ips ", "IPS ")
    t = t.replace("It ", "Information Technology ")
    t = t.replace("Iv ", "IV ")
    t = t.replace("Jnt ", "Joint ")
    t = t.replace("Mgmt ", "Management ")
    t = t.replace("Mgr ", "Manager ")
    t = t.replace("Mgt ", "Management ")
    t = t.replace("Mlti ", "Multi ")
    t = t.replace("Mlti-ctr ", "Multicenter ")
    t = t.replace("Mltictr ", "Multicenter ")
    t = t.replace("Mri ", "MRI ")
    t = t.replace("Mstr ", "Master ")
    t = t.replace("Multi-center ", "Multicenter ")
    t = t.replace("Multi-ctr ", "Multicenter ")
    t = t.replace("Nih ", "NIH ")
    t = t.replace("Nmr ", "NMR ")
    t = t.replace("Nsf ", "NSF ")
    t = t.replace("Of ", "of ")
    t = t.replace("On ", "on ")
    t = t.replace("Or ", "or ")
    t = t.replace("Open-labeled ", "Open-label ")
    t = t.replace("Opn-lbl ", "Open-label ")
    t = t.replace("Opr ", "Operator ")
    t = t.replace("Phas ", "Phased ")
    t = t.replace("Php ", "PHP ")
    t = t.replace("Phs ", "PHS ")
    t = t.replace("Pk/pd ", "PK/PD ")
    t = t.replace("Pky ", "P. K. Yonge ")
    t = t.replace("Pky ", "PK Yonge ")
    t = t.replace("Plcb-ctrl ", "Placebo-controlled ")
    t = t.replace("Plcbo ", "Placebo ")
    t = t.replace("Plcbo-ctrl ", "Placebo-controlled ")
    t = t.replace("Postdoc ", "Postdoctoral ")
    t = t.replace("Pract ", "Practitioner ")
    t = t.replace("Pres5 ", "President 5 ")
    t = t.replace("Pres6 ", "President 6 ")
    t = t.replace("Prg ", "Programs ")
    t = t.replace("Prof ", "Professor ")
    t = t.replace("Prog ", "Programmer ")
    t = t.replace("Progs ", "Programs ")
    t = t.replace("Prov ", "Provisional ")
    t = t.replace("Psr ", "PSR ")
    t = t.replace("Radiol ", "Radiology ")
    t = t.replace("Rcv ", "Receiving ")
    t = t.replace("Rdmzd ", "Randomized ")
    t = t.replace("Rep ", "Representative ")
    t = t.replace("Res ", "Research ")
    t = t.replace("Ret ", "Retirement ")
    t = t.replace("Reu ", "REU ")
    t = t.replace("Rna ", "RNA ")
    t = t.replace("Rndmzd ", "Randomized ")
    t = t.replace("Roc-124 ", "ROC-124 ")
    t = t.replace("Rsch ", "Research ")
    t = t.replace("Saf ", "SAF ")
    t = t.replace("Saf/eff ", "Safety and Efficacy ")
    t = t.replace("Sch ", "School ")
    t = t.replace("Ser ", "Service ")
    t = t.replace("Sfwmd ", "SFWMD ")
    t = t.replace("Sle ", "SLE ")
    t = t.replace("Sntc ", "SNTC ")
    t = t.replace("Spec ", "Specialist ")
    t = t.replace("Spv ", "Supervisor ")
    t = t.replace("Sr ", "Senior ")
    t = t.replace("Stdy ", "Study ")
    t = t.replace("Subj ", "Subject ")
    t = t.replace("Supp ", "Support ")
    t = t.replace("Supt ", "Superintendant ")
    t = t.replace("Supv ", "Supervisor ")
    t = t.replace("Svc ", "Services ")
    t = t.replace("Svcs ", "Services ")
    t = t.replace("Tch ", "Teaching ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Technol ", "Technologist ")
    t = t.replace("Teh ", "The ")
    t = t.replace("To ", "to ")
    t = t.replace("Tv ", "TV ")
    t = t.replace("Uf ", "UF ")
    t = t.replace("Ufrf ", "UFRF ")
    t = t.replace("Univ ", "University ")
    t = t.replace("Us ", "US ")
    t = t.replace("Vis ", "Visiting ")
    t = t.replace("Vp ", "Vice President ")
    t = t.replace("Wuft-Fm ", "WUFT-FM ")
    t = t.replace(" @", "/") # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" !", ",") # restore ,
    t = t.replace(" #", "-") # restore -
    return t[0].upper() + t[1:-1] # Take off the trailing space

# Driver program starts here

source_csv = read_csv('test_unicode.txt')
print source_csv

source_grant = source_csv[1]
vivo_grant_uri = vt.find_vivo_uri("ufVivo:psContractNumber",source_grant['AwardID'])
vivo_grant = vt.get_grant(vivo_grant_uri)

source_title= improve_grant_title(source_grant['Title'])

print vivo_grant['title']['value'],type(vivo_grant['title']['value'])
print source_title,type(source_title)

[add,sub] = vt.update_data_property(vivo_grant_uri,"rdfs:label",\
                                    vivo_grant['title'],source_title)

add_file = codecs.open('test_unicode_add.rdf',mode='w',encoding='ascii',errors='xmlcharrefreplace')
sub_file = codecs.open('test_unicode_sub.rdf',mode='w',encoding='ascii',errors='xmlcharrefreplace')

add_file.write(vt.rdf_header())
sub_file.write(vt.rdf_header())

add_file.write(add)
sub_file.write(sub)

add_file.write(vt.rdf_footer())
add_file.close()

sub_file.write(vt.rdf_footer())
sub_file.close()

