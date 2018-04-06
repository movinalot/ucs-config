"""
ucs-config.py

Purpose:
    Manage UCS Objects from configuration file, using dynamic module loading.
    All Configuration settings and module requirements come from a JSON/YAML
    file.

    Configure/Manage UCS Manager and Cisco IMC from JSON/YAML

Author:
    John McDonough (jomcdono@cisco.com)
    Cisco Systems, Inc.
"""

from importlib import import_module
import json
import logging
import os
import sys
import yaml

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def traverse(managed_object, mo=''):
    logging.info(managed_object['class'])
    logging.debug(managed_object['module'])
    logging.debug(managed_object['properties'])

    mo_module = import_module(managed_object['module'])
    mo_class = getattr(mo_module, managed_object['class'])

    if 'parent_mo_or_dn' not in managed_object['properties']:
        managed_object['properties']['parent_mo_or_dn'] = mo

    mo = mo_class(**managed_object['properties'])
    logging.debug(mo)

    handle.add_mo(mo, modify_present = True)

    if 'children' in managed_object:
        for child in managed_object['children']:
            traverse(child, mo)

if __name__ == '__main__':

    filename = os.path.join(sys.path[0], sys.argv[1])

    logging.info('Reading config file: ' + filename)
    try:
        with open(filename, 'r') as file:
            if filename.endswith('.json'):
                config = json.load(file)
            elif filename.endswith('.yml'):
                config = yaml.load(file)
            else:
                logging.info('Unsupported file extension for configuration ' +
                'file: ' + filename)
    
    except IOError as eError:
        sys.exit(eError)

    mo_module = import_module(config['connection']['module'])
    obj_class = config['connection']['class']
    mo_class = getattr(mo_module, obj_class)

    handle = mo_class(**config['connection']['properties'])
    handle.login()

    for managed_object in config['objects']:
        traverse(managed_object)
        if config['connection']['commit-buffer']:
            handle.commit()

    handle.logout()