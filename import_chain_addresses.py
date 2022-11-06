#!/usr/bin/env python
"""
Script to help reimport or update various chain address data sources.
"""
import importlib
from argparse import ArgumentParser
from os import environ, path
from sys import exit

from rich_argparse_plus import RichHelpFormatterPlus

from ethecycle.chain_addresses.address_db import drop_and_recreate_tables
from ethecycle.chain_addresses.db import CHAIN_ADDRESSES_DB_FILE_NAME, CHAIN_ADDRESSES_DB_PATH
from ethecycle.chain_addresses.importers import rebuild_chain_addresses_db
from ethecycle.config import Config
from ethecycle.util.filesystem_helper import SCRIPTS_DIR
from ethecycle.util.logging import console, set_log_level
from ethecycle.util.string_constants import DEBUG

REBUILD_ALL = 'ALL'
RESET_DB = 'RESET_DB'
IMPORT_PREFIX = 'import_'
IMPORTER_MODULE_STR = 'ethecycle.chain_addresses.importers'
IMPORTERS_MODULE = importlib.import_module(IMPORTER_MODULE_STR)
PREBUILT_CHAIN_ADDRESS_DB_PATH = path.join(SCRIPTS_DIR, 'docker', 'container_files', CHAIN_ADDRESSES_DB_FILE_NAME)

IMPORTER_METHODS = [REBUILD_ALL, RESET_DB] + [
    import_method.removeprefix(IMPORT_PREFIX)
    for import_method in dir(IMPORTERS_MODULE)
    if import_method.startswith(IMPORT_PREFIX)
]


# Argument parser
RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description=f"Reimport a chain address data sources. Select '{REBUILD_ALL}' to rebuild DB from scratch, '{RESET_DB}' to drop and recreate empty DB."
)

parser.add_argument('importer_method',
                    help='chain address importer method to call',
                    choices=IMPORTER_METHODS)

parser.add_argument('-s', '--suppress-warnings', action='store_true',
                    help='suppress DB collision warnings')

parser.add_argument('-D', '--debug', action='store_true',
                    help='show debug level log output')

args = parser.parse_args()

if args.debug:
    Config.debug = True
    set_log_level(DEBUG)

if args.suppress_warnings:
    Config.suppress_chain_address_db_collision_warnings = True

if args.importer_method == REBUILD_ALL:
    rebuild_db_arg = environ.get('REBUILD_CHAIN_ADDRESS_DB')

    if rebuild_db_arg == 'copy_prebuilt_address_db':
        if path.isfile(CHAIN_ADDRESSES_DB_PATH):
            console.print(f"Skipping rebuild: '{CHAIN_ADDRESSES_DB_PATH}' exists and REBUILD_CHAIN_ADDRESS_DB: {rebuild_db_arg}")
            exit()
        else:
            console.print(f"Prebuilt DB requested but '{CHAIN_ADDRESSES_DB_PATH}' does not exist so proceeding w/build...")

    rebuild_chain_addresses_db()
elif args.importer_method == RESET_DB:
    drop_and_recreate_tables()
else:
    getattr(IMPORTERS_MODULE, IMPORT_PREFIX + args.importer_method)()
