#!/bin/bash
# Import data scraped from Dune Analytics dashboards.

python -c 'from ethecycle.data.wallet_labels.wallets_from_dune_importer import import_wallets_from_dune; import_wallets_from_dune()'
