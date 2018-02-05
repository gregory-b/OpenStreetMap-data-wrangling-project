# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


# READ HOUSENUMBERS IN DIFFERENT FORMATS AND WRITE THEM IN A UNIFORM WAY

housenumber_re = re.compile(r'([b]{2})|(\d{1,3}\skm)|(\d{1,3})([a-zA-Z])?[, /-]*([a-zA-Z])?(\d{1,3})*([a-zA-Z])*', re.IGNORECASE)
# <tag k="addr:housenumber" v="12/f"/>  ==> 12F,  "A" ==> skip, 7, 9 ==> 7,9, 13, 13A ==> 13,13A, 63 km ==> 63 km


def audit_housenumber(housenumber):
    mo = housenumber_re.search(housenumber)
    if mo:
        try:
            return (mo.group()).upper()
        except AttributeError:
            return ''
    else:
        #print "NOT A VALID HOUSENUMBER"
        return '' # if not a match object, return empty string
    

    
remove_chars = set('/ ')
def housenumberUpdate(housenumber):
    new_housenum = audit_housenumber(housenumber)
    if new_housenum:  # None is not True...
        if new_housenum[-3:] == ' km': # if mo result is "... km", leave as is (with space, uncapitalized)
            return new_housenum
        else:
            # a workaround, because 'return new_housenum.translate(None, '/ ').upper()' doesn't work:
            return (''.join([char for char in new_housenum if char not in remove_chars])).upper()
            
            
