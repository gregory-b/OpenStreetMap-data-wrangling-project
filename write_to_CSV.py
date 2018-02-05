#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import housenumber_update2 as hn2
import phone_update2 as p2
import source_update2 as s2
import postcode_update2 as pc2
import name_update2 as n2
import cerberus
import schema

work_OSM_file = 'se_slovenia.osm'

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema


NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    node_tags_fields_list = []
    zip_node_tags_list = []
    if element.tag == "node":
        for k,v in element.items():
            if k in node_attr_fields:
                node_attribs[k] = v
        for child in element:
            if child.tag == 'tag':
                match_object = PROBLEMCHARS.search(child.attrib["k"])
                if match_object:
                    continue     # TO IGNORE THE ENTIRE TAG
                else:
                    string_child_k = child.attrib["k"]                             #
                    string_child_k0, string_child_k1, string_child_k2 = '', '', '' # define new string objects
                    
                    if len(string_child_k.split(':', 1)) == 1:
                        child.attrib["k"] = string_child_k
                        default_tag_type = 'regular'
                    else:                                                   
                        string_child_k0 = string_child_k.split(':', 1)[0]    
                        string_child_k1 = string_child_k.split(':', 1)[1]
                        child.attrib["k"] = string_child_k1
                        default_tag_type = string_child_k0
                # UPDATE NODES
                if child.attrib["k"] == 'name':
                    node_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                        n2.nameUpdate(child.attrib["v"]), default_tag_type]                
                
                elif child.attrib["k"] == 'postcode':
                    node_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                        pc2.postcodeUpdate(child.attrib["v"]), default_tag_type]

                elif child.attrib["k"] == 'phone' or child.attrib["k"] == 'contact:phone' \
                    or child.attrib["k"] == 'fax' or child.attrib["k"] == 'contact:fax':
                    node_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                             p2.phoneUpdate(child.attrib["v"]), default_tag_type]

                elif child.attrib["k"] == 'housenumber':
                    node_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                            hn2.housenumberUpdate(child.attrib["v"]), default_tag_type]

                elif child.attrib["k"] == 'source' and default_tag_type == 'regular':
                    node_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                             s2.sourceUpdate(child.attrib["v"]), default_tag_type]
                # END UPDATE NODES
                else:
                    node_tags_fields_list = [element.attrib["id"], child.attrib["k"], child.attrib["v"], default_tag_type]

                zip_node_tags_list = zip(NODE_TAGS_FIELDS, node_tags_fields_list)
                tags += [dict(zip_node_tags_list)]
        #pprint.pprint({'node': node_attribs, 'node_tags': tags})
        return {'node': node_attribs, 'node_tags': tags}
        
    # SECOND PART OF THE CODE
    way_tags_fields_list = []
    zip_way_tags_list = []
    if element.tag == "way":
        for k,v in element.items():
            if k in way_attr_fields:
                way_attribs[k] = v
        for index, child in enumerate(element):
            if child.tag == 'tag':
                match_object = PROBLEMCHARS.search(child.attrib["k"])
                if match_object:
                    continue     # TO IGNORE THE ENTIRE TAG
                else:
                    string_child_k = child.attrib["k"]                             #
                    string_child_k0, string_child_k1, string_child_k2 = '', '', '' # define new string objects
                    
                    if len(string_child_k.split(':', 1)) == 1:
                        child.attrib["k"] = string_child_k
                        default_tag_type = 'regular' 
                    else:
                        string_child_k0 = string_child_k.split(':', 1)[0]
                        string_child_k1 = string_child_k.split(':', 1)[1]
                        child.attrib["k"] = string_child_k1
                        default_tag_type = string_child_k0 
                # UPDATE WAYS
                if child.attrib["k"] == 'name':
                    node_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                        n2.nameUpdate(child.attrib["v"]), default_tag_type]
                
                elif child.attrib["k"] == 'postcode':
                    way_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                            n2.nameUpdate(child.attrib["v"]), default_tag_type]
                    
                elif child.attrib["k"] == 'phone' or child.attrib["k"] == 'contact:phone' \
                    or child.attrib["k"] == 'fax' or child.attrib["k"] == 'contact:fax':
                    way_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                            p2.phoneUpdate(child.attrib["v"]), default_tag_type]
 
                elif child.attrib["k"] == 'addr:housenumber':
                    way_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                            hn2.housenumberUpdate(child.attrib["v"]), default_tag_type]
 
                elif child.attrib["k"] == 'source' and default_tag_type == 'regular':
                    way_tags_fields_list = [element.attrib["id"], child.attrib["k"], 
                                            s2.sourceUpdate(child.attrib["v"]), default_tag_type]
                # END UPDATE WAYS
                else:
                    way_tags_fields_list = [element.attrib["id"], child.attrib["k"], child.attrib["v"], default_tag_type]

                zip_way_tags_list = zip(WAY_TAGS_FIELDS, way_tags_fields_list)
                tags += [dict(zip_way_tags_list)]

            if child.tag == 'nd':
                way_tags_fields_list = [element.attrib["id"], child.attrib["ref"], index]
                zip_way_tags_fields_list = zip(WAY_NODES_FIELDS, way_tags_fields_list)
                way_nodes += [dict(zip_way_tags_fields_list)]
                
        #pprint.pprint({'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags})
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}




# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(work_OSM_file, validate=False)
