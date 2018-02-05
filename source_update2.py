# -*- coding: utf-8 -*-


import xml.etree.cElementTree as ET
#from collections import defaultdict
import re
import pprint


sources_expected = ["Bing", "DigitalGlobe", "MapBox", "U.S.", "GPS", "survey", "Yahoo", "GURS", "RABA-KGZ",
            "gps-planine.com", "ourairports.com", "commons.wikimedia.org"]

sources_mapping = {"Bing lowres":"Bing", "Bing;GPS":"Bing", "Bing;survey":"Bing", 
           "Bing;survey;Internet":"Bing", "bing": "Bing",
           "DigitalGlobe; http://uskok-sosice.hr/zumberak-uskocko-gorje/":"DigitalGlobe", 
           "DigitalGlobe; local_knowledge":"DigitalGlobe", "orbview":"DigitalGlobe", 
           "garmin-60csx":"GPS", "gps":"GPS", "TZKZ gpx log":"GPS",
           "U.S":"U.S.", "U.S. Defense Mapping Agency":"U.S.", "ncdc.noaa.gov":"U.S.", "landsat":"U.S.",
           "MapBox;survey":"MapBox", "Mapbox":"MapBox", 
           "survey;infoboard":"survey",
           "http://gps-planine.com":"gps-planine.com",
           "http://commons.wikimedia.org/wiki/File:Croatian_counties.png":"commons.wikimedia.org", 
           }


def sourceUpdate(source):
    if source not in sources_expected:
        source = sources_mapping[source]
    return source