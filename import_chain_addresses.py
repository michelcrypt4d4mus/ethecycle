#!/usr/bin/env python
"""
Script to help reimport or update various chain address data sources.
"""
import importlib
from argparse import ArgumentParser

from rich_argparse_plus import RichHelpFormatterPlus

from ethecycle.chain_addresses.importers import rebuild_chain_addresses_db
from ethecycle.config import Config
from ethecycle.util.logging import console, set_log_level
from ethecycle.util.string_constants import DEBUG

REBUILD_ALL = 'ALL'
IMPORT_PREFIX = 'import_'
IMPORTER_MODULE_STR = 'ethecycle.chain_addresses.importers'
IMPORTERS_MODULE = importlib.import_module(IMPORTER_MODULE_STR)

IMPORTER_METHODS = [REBUILD_ALL] + [
    import_method.removeprefix(IMPORT_PREFIX)
    for import_method in dir(IMPORTERS_MODULE)
    if import_method.startswith(IMPORT_PREFIX)
]


# Argument parser
RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description="Reimport or update various chain address data sources. Select 'ALL' to rebuild DB from scratch."
)

parser.add_argument('importer_method',
                    help='chain address importer method to call',
                    choices=IMPORTER_METHODS)

parser.add_argument('-D', '--debug', action='store_true',
                    help='show debug level log output')

args = parser.parse_args()

if args.debug:
    Config.debug = True
    set_log_level(DEBUG)

if args.importer_method == REBUILD_ALL:
    rebuild_chain_addresses_db()
else:
    getattr(IMPORTERS_MODULE, IMPORT_PREFIX + args.importer_method)()
