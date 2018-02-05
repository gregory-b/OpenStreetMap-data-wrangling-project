# -*- coding: utf-8 -*-

# READ PHONE NUMBERS IN DIFFERENT FORMATS AND WRITE THEM IN AN UNIFORM WAY:






import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


phone_num_re = re.compile(r'([0+]{1,2})(38[5|6] ?\d{1,3} ?\d{2,3} ?\d{2,3} ?\d{1,3})') # with grouped prefix, working

phone_valid_exceptions_dict = { '+ 386 41 726 602':'+38641726602', '041 518887':'+38641518887', 
                               '+386(0)7 393 45 20':'+38673934520', '041 290 990':'+38641290990', 
                               '041 915 688':'+38641915688', '041 609 172':'+38641609172' 
                              }


def phoneUpdate(phone):
    mo_phone_num = phone_num_re.search(phone)
    try:
        uniform_number = ''.join([mo_phone_num.group(1).replace('00', '+'), mo_phone_num.group(2).replace(' ', '')])
        if uniform_number[4] == '0':
            uniform_number = uniform_number[:4] + uniform_number[5:]  # to remove possible '0' after the country code
        return uniform_number  
    except AttributeError:
        if phone in phone_valid_exceptions_dict:
            uniform_number = phone_valid_exceptions_dict[phone]
            return uniform_number
        else:
        #print "INVALID PHONE NUMBER VALUE: '", phone, "'"
            return ''