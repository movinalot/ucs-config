"""
ucs-config.py

Purpose:
    Configure UCS Manager from JSON file, using dynamic module loading.
    All Configuration settings and module reqiorements come from the 
    JSON file.

Author:
    John McDonough (jomcdono@cisco.com)
    Cisco Systems, Inc.
"""

import sys
import json
import urllib2
from importlib import import_module
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucssession import UcsException
#from ucsmsdk.ucscoreutils import get_meta_info



import logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def e_exit(e_handle, e_exception, e_message, e_host = ''):
    """ exception based script exit """
    
    logging.info(e_exception)
    logging.info(e_message)

    if e_handle != None and e_handle.cookie:
        logging.info("Host: " + e_host \
            + " - attempting disconnection from API endpoint")
        if e_handle.logout():
            logging.info("Host: " + e_host \
                + " - successful disconnection from API endpoint")
        else:
            logging.info("Host: " + e_host \
                + " - unsuccessful disconnection from API endpoint")
    logging.info("Exiting on script error")
    sys.exit(1)

def main(argv):
    """ Process JSON settings to configure UCS Manager """

    filename = 'Y:\\Documents\\src\\ucs\\ucs-config\\python\\ucsm\\ucsm.json'

    #Read JSON data into the settings_file variable
    logging.info("Reading JSON File: " + filename)
    try:
        with open(filename, "r") as file:
            settings_file = json.load(file)
    except IOError as eError:
        e_exit(None,eError,"Unable to open JSON settings file",None)


    ucsm_ssl = False
    if ("secure" in settings_file["connection"] and
        settings_file["connection"]["secure"]):
        ucsm_ssl = True

    ucsm_host = settings_file["connection"]["ip"]
    ucsm_user = settings_file["connection"]["username"]
    ucsm_pass = settings_file["connection"]["password"]

    handle = UcsHandle(ucsm_host,
                       ucsm_user,
                       ucsm_pass,
                       secure = ucsm_ssl)

    try:
        logging.info("UCSM: " 
                        + ucsm_host +
                        " - attempting connection to API endpoint")
        if handle.login() == True:
            logging.info("UCSM: " 
                        + ucsm_host +
                        " - successful connection to API endpoint")

    except urllib2.URLError as eError:
        e_exit(handle,eError,"UCSM: " + ucsm_host
                + " - cannot connect to API endpoint",ucsm_host)
    except UcsException as eError:
        e_exit(handle,eError,"UCSM: " + ucsm_host
                + " - cannot connect to API endpoint",ucsm_host)

    ucs_objects = settings_file["ucs_objects"]
    for ucs_object in ucs_objects:

        if ucs_object["mode"] == "create":

            mo_module = import_module(ucs_object["module"])
            obj_class = ucs_object["class"]
            mo_class = getattr(mo_module, obj_class)

            object_defs = ucs_object["objects"]

            for object_def in object_defs:
                mo = mo_class(**object_def["properties"])
                handle.add_mo(mo, modify_present=True)

                logging.debug(object_def)
                if "message" in object_def:
                    logging.info(object_def["message"])

        elif ucs_object["mode"] == "update":

            object_def =  ucs_object["object"]
            mo = handle.query_dn(object_def["dn"])

            for object_prop in object_def["properties"]:
                setattr(mo, object_prop, object_def["properties"][object_prop] )

            handle.add_mo(mo, modify_present=True)

            logging.debug(object_def)
            if "message" in object_def:
                logging.info(object_def["message"])
        
        handle.commit()

    handle.logout()

if __name__ == "__main__":
   main(sys.argv[1:])

