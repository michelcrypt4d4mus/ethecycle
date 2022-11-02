from ethecycle.config import Config
from ethecycle.data.chain_addresses.address_db import drop_and_recreate_tables
from ethecycle.data.chain_addresses.coin_market_cap_repo_importer import \
    import_coin_market_cap_repo_addresses
from ethecycle.data.chain_addresses.ethereum_lists_repo_importer import import_ethereum_lists_addresses
from ethecycle.data.chain_addresses.etherscrape_importer import import_etherscrape_chain_addresses
from ethecycle.data.chain_addresses.hardcoded_addresses import import_hardcoded_addresses
from ethecycle.data.chain_addresses.wallets_from_dune_importer import \
    import_wallets_from_dune


def rebuild_chain_addresses_db():
    Config.skip_load_from_db = True
    """Drop all tables and rebuild from source data."""
    drop_and_recreate_tables()
    import_hardcoded_addresses()
    import_coin_market_cap_repo_addresses()
    import_etherscrape_chain_addresses()
    import_wallets_from_dune()
    Config.skip_load_from_db = False
