import pandas as pd

df = pd.read_csv('data/mints_burns.csv')
df['amount'] = df['amount'].replace('[\\$,]', '', regex=True).astype(float)
df['amount_tron'] = df['amount']
df['amount_ethereum'] = df['amount']

df.loc[df['Chain'] != 'Ethereum', 'amount_ethereum'] = 0
df.loc[df['Chain'] != 'Tron', 'amount_tron'] = 0

df['ethereum_market_cap'] = df['amount_ethereum'].cumsum(skipna=False)
df['tron_market_cap'] = df['amount_tron'].cumsum(skipna=False)

# Strip out useless columns
df = df[['DateTime', 'Chain', 'amount', 'Expected Market Cap', 'ethereum_market_cap', 'tron_market_cap']]
df.to_csv('mints_burns_with_cumulative_sum.csv')
