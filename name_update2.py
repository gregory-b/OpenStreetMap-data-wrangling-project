# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import re

names_exceptions = {"Sv. Jelena":"Sveta Jelena", "9 ~ Cikava / M. Cikava":"9 Cikava / Mala Cikava",   
                    "PGD ŠALKA VAS":"PGD Šalka vas", "Sv.Gere":"Svete Gere", "LInhartova ulica":"Linhartova ulica",
                    "Radenci– ":"Radenci–", "47282 Kamanje":"Kamanje", "51311 Skrad":"Skrad",
                    "51312 Brod Moravice":"Brod Moravice", "51328 Lukovdol":"Lukovdol", "47272 Ribnik":"Ribnik", 
                    "51325 Moravice":"Moravice", "TGH, d.o.o":"TGH, d.o.o.", "C.brigad":"Cesta brigad", 
                    "kapelica Sv.Gere":"kapelica Svete Gere", "Novo mesto C.brigad":"Novo mesto Cesta brigad" 
                   }

names_mapping = {"svetog":"Svetog", "svete":"Svete", "Crkva":"crkva", "SMUK":"Smuk", "resa":"Resa", 
                 "gim.":"gimnazija", "teh.":"tehnični ", "Tuš":"TUŠ", " Xv ":" XV. ", " Ac":" AC", 
                 "Sv.":"Sveti", "sv.":"Sveti", "St.":"Saint", "NM":"Novo mesto", "J.": "Jurovski", "M. ":"Mali ", 
                 " - ":"-", " ~ ":" ", " ~":" ", " . ":"-", "c.":"cesta", "C.":"Cesta ", "G.":"Gornje"                                
                }


new_name = []
def nameUpdate(name):
    if name in names_exceptions:
        return names_exceptions[name]
    else:   #  see:  https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
        substrings = sorted(names_mapping, key=len, reverse=True)  # to match the longer strings first
        substr_re = re.compile('|'.join(map(re.escape, substrings)))  # replace any of the substrings
        return substr_re.sub(lambda mo: names_mapping[mo.group(0)], name)  # for each match, replace with string from mapping