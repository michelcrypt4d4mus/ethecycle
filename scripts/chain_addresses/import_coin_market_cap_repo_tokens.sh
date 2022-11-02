#!/bin/bash
# Pull a GH repo with all the coins/tokens/whatever that CoinMarketCap has listed as of some not too
# distant date and then extract that information to the chain_addresses.db.

python -c 'from ethecycle.data.chain_addresses.coin_market_cap_repo_importer import import_coin_market_cap_repo_addresses; import_coin_market_cap_repo_addresses()'
