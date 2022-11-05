"""
Test all the importers except the big ones
"""
from os import pardir, path

from ethecycle.config import Config
from ethecycle.chain_addresses.address_db import get_db_connection

from ethecycle.chain_addresses import github_data_source
from ethecycle.chain_addresses.importers.coin_market_cap_repo_importer import import_coin_market_cap_repo_addresses
from ethecycle.chain_addresses.importers.cryptoscamdb_addresses_importer import import_cryptoscamdb_addresses
from ethecycle.chain_addresses.importers.etherscrape_importer import import_etherscrape_chain_addresses
from ethecycle.chain_addresses.importers.hardcoded_addresses_importer import import_hardcoded_addresses
from ethecycle.chain_addresses.importers.my_ether_wallet_repo_importer import import_my_ether_wallet_addresses
from ethecycle.chain_addresses.importers.trustwallet_assets_importer import import_trust_wallet_repo
from ethecycle.chain_addresses.importers.wallets_from_dune_importer import import_wallets_from_dune
from ethecycle.chain_addresses.importers.w_mcdonald_etherscan_repo_importer import import_w_mcdonald_etherscan_addresses
from ethecycle.util.filesystem_helper import PROJECT_ROOT_DIR, SCRIPTS_DIR

# TODO: this is a grotesque hack
# github_data_source.GIT_PULL_SCRIPT = path.realpath(
#     path.join(PROJECT_ROOT_DIR, pardir, 'scripts', 'chain_addresses', 'git_clone_if_missing.sh')
# )


def test_importers():
    """Drop all tables and rebuild from source data."""
    Config.skip_load_from_db = True
    import_hardcoded_addresses()
    import_cryptoscamdb_addresses()
    import_etherscrape_chain_addresses()
    import_my_ether_wallet_addresses()
    import_trust_wallet_repo()
    import_wallets_from_dune()
    import_w_mcdonald_etherscan_addresses()
    get_db_connection().disconnect()
    Config.skip_load_from_db = False


@pytest.mark.slow
def test_slow_importers():
    import_coin_market_cap_repo_addresses()
