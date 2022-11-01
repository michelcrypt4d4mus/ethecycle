#!/bin/bash
# Pull a GH repo with all the coins/tokens/whatever that CoinMarketCap has listed as of some not too
# distant date and then extract that information to a CSV.

GIT_CLONE_IF_MISSING="$(dirname $0)/git_clone_if_missing.sh"
REPO_DIR=$($GIT_CLONE_IF_MISSING $COIN_MARKET_CAP_DATA_GITHUB_REPO)

cd "$REPO_DIR"
echo "REPO_DIR: $REPO_DIR, PWD: $PWD"
echo "rm -fr Download/chart Download/csv Download/summary.csv Download/summaryOnlyTrue.csv WhitePaper .git"
cd -

python -c 'from ethecycle.extract.wallet_data.cmc_data import extract_coin_market_cap_repo_data_to_wallets_db; extract_coin_market_cap_repo_data_to_wallets_db()'
