#!/usr/bin/env python
"""
Script to help reimport or update various chain address data sources.
"""
import importlib
from argparse import ArgumentParser

from rich_argparse_plus import RichHelpFormatterPlus

IMPORTER_MODULE_STR = 'ethecycle.chain_addresses.importers'
IMPORTERS_MODULE = importlib.import_module(IMPORTER_MODULE_STR)
IMPORTER_METHODS = [importer for importer in dir(IMPORTERS_MODULE) if importer.startswith('import_')]


# Argument parser
RichHelpFormatterPlus.choose_theme('prince')

parser = ArgumentParser(
    formatter_class=RichHelpFormatterPlus,
    description="Reimport or update various chain address data sources."
)

parser.add_argument('importer_method',
                    help='chain address importer method to call',
                    choices=IMPORTER_METHODS)

args = parser.parse_args()

getattr(IMPORTERS_MODULE, args.importer_method)()
