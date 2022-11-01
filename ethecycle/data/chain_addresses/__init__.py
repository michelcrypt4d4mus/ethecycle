from ethecycle.data.chain_addresses.address_db import drop_and_recreate_tables
from ethecycle.data.chain_addresses.coin_market_cap_repo_importer import \
    import_coin_market_cap_repo_addresses
from ethecycle.data.chain_addresses.wallets_from_dune_importer import \
    import_wallets_from_dune
from ethecycle.util.logging import console


def rebuild_chain_addresses_db():
    """Drop all tables and rebuild from source data."""
    drop_and_recreate_tables()
    import_coin_market_cap_repo_addresses()
    import_wallets_from_dune()
