#!/bin/bash
# Pull a GH repo with all the coins/tokens/whatever that CoinMarketCap has listed as of some not too
# distant date and then extract that information to a CSV.
GIT_CLONE_IF_MISSING="$(dirname $0)/git_clone_if_missing.sh"
REPO_DIR=$($GIT_CLONE_IF_MISSING https://github.com/tttienthinh/CoinMarketCap.git)

pushd "$REPO_DIR"
rm -fr Download/chart Download/csv Download/summary.csv Download/summaryOnlyTrue.csv WhitePaper .git
popd

python -c 'from ethecycle.extract.wallet_data.cmc_data import extract_coin_market_cap_data_to_csv; extract_coin_market_cap_data_to_csv()'
