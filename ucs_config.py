"""
ucs_config.py

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

# pylint: disable=invalid-name,redefined-outer-name

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def traverse(managed_object, mo=''):
    """
        Traverse the configuration this function will be called
        recursively until the end of the configuration is reached
    """
    logging.info(managed_object['class'])
    logging.debug(managed_object['module'])
    logging.debug(managed_object['properties'])

    mo_module = import_module(managed_object['module'])
    mo_class = getattr(mo_module, managed_object['class'])

    if 'parent_mo_or_dn' not in managed_object['properties']:
        managed_object['properties']['parent_mo_or_dn'] = mo

    mo = mo_class(**managed_object['properties'])
    logging.debug(mo)

    HANDLE.add_mo(mo, modify_present=True)

    if 'children' in managed_object:
        for child in managed_object['children']:
            traverse(child, mo)

if __name__ == '__main__':

    FILENAME = os.path.join(sys.path[0], sys.argv[1])

    logging.info('Reading config file: %s', FILENAME)
    try:
        with open(FILENAME, 'r') as file:
            if FILENAME.endswith('.json'):
                config = json.load(file)
            elif FILENAME.endswith('.yml'):
                config = yaml.load(file, Loader=yaml.FullLoader)
            else:
                logging.info(
                    'Unsupported file extension for configuration file: %s'
                    , FILENAME
                    )

    except IOError as io_error:
        sys.exit(io_error)

    mo_module = import_module(config['connection']['module'])
    obj_class = config['connection']['class']
    mo_class = getattr(mo_module, obj_class)

    HANDLE = mo_class(**config['connection']['properties'])
    HANDLE.login()

    for managed_object in config['objects']:
        traverse(managed_object)
        if config['connection']['commit-buffer']:
            HANDLE.commit()

    HANDLE.logout()
