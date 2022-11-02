from ethecycle.config import Config
from ethecycle.chain_addresses.address_db import drop_and_recreate_tables
from ethecycle.chain_addresses.importers.coin_market_cap_repo_importer import \
    import_coin_market_cap_repo_addresses
from ethecycle.chain_addresses.importers.ethereum_lists_repo_importer import \
    import_ethereum_lists_addresses
from ethecycle.chain_addresses.importers.etherscrape_importer import import_etherscrape_chain_addresses
from ethecycle.chain_addresses.importers.hardcoded_addresses import import_hardcoded_addresses
from ethecycle.chain_addresses.importers.my_ether_wallet_repo_importer import import_my_ether_wallet_addresses
from ethecycle.chain_addresses.importers.wallets_from_dune_importer import \
    import_wallets_from_dune


def rebuild_chain_addresses_db():
    """Drop all tables and rebuild from source data."""
    Config.skip_load_from_db = True
    import_my_ether_wallet_addresses()
    return
    drop_and_recreate_tables()
    import_hardcoded_addresses()
    import_coin_market_cap_repo_addresses()
    import_ethereum_lists_addresses()
    import_etherscrape_chain_addresses()
    import_wallets_from_dune()
    Config.skip_load_from_db = False
