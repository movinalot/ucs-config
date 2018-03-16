"""
ucs-manage.py

Purpose:
    Manage UCS Management from JSON file, using dynamic module loading.
    All Configuration settings and module reqiorements come from the 
    JSON/YAML/XML file.

    Configure/Manage UCS Manager and Cisco IMC from JSON/YAML/XML

Author:
    John McDonough (jomcdono@cisco.com)
    Cisco Systems, Inc.
"""

import sys
import json
import urllib2
from importlib import import_module
import logging

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def traverse(managed_object, mo=""):
    logging.info(managed_object['class'])

    mo_module = import_module(managed_object["module"])
    mo_class = getattr(mo_module, managed_object["class"])

    logging.debug(managed_object["module"])
    logging.debug(managed_object["properties"])

    if "parent_mo_or_dn" not in managed_object["properties"]:
        managed_object["properties"]["parent_mo_or_dn"] = mo

    logging.debug(mo)
    mo = mo_class(**managed_object["properties"])
    handle.add_mo(mo, modify_present = True)

    if "children" in managed_object:
        for child in managed_object['children']:
            traverse(child, mo)

if __name__ == '__main__':

    filename = 'Y:\\Documents\\src\\ucs\\ucs-config\\python\\ucsm\\ucsm.json'

    logging.info("Reading settings file: " + filename)
    try:
        with open(filename, "r") as file:
            settings = json.load(file)
    
    except IOError as eError:
        e_exit(None,eError,"Unable to open settings file",None)


    mo_module = import_module(settings["connection"]["module"])
    obj_class = settings["connection"]["class"]
    mo_class = getattr(mo_module, obj_class)

    handle = mo_class(**settings["connection"]["properties"])
    handle.login()

    for managed_object in settings['objects']:
        traverse(managed_object)
        handle.commit()

    handle.logout()