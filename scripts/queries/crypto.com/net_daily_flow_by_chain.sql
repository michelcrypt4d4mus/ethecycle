WITH address AS (
  SELECT
    address,
    label
  from (
    values
      ('0x72A53cDBBcc1b9efa39c834A540550e23463AAcB', 'Crypto.com 1'),
      ('0x46340b20830761efd32832a74d7169b29feb9758', 'Crypto.com 2'),
      ('0xcffad3200574698b78f32232aa9d63eabd290703', 'Crypto.com 3'),
      ('0x7758e507850da48cd47df1fb5f875c23e3340c50', 'Crypto.com 4'),
      ('0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b', 'CRONOS Token'),
      ('0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3', 'Crypto.com 5'),
      ('0xb63b606ac810a52cca15e44bb630fd42d8d1d83d', 'Crypto.com: MCO Token')
  ) AS t(address, label)
),


ethereum_token_flow AS (
  with erc20_token_flow AS (
    SELECT
      'ethereum'  AS blockchain,
      contract_address AS token_address,
      date_trunc('minute', evt_block_time) AS block_minute,
      -value AS amount
    FROM erc20_ethereum.evt_Transfer
      INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
       LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
    WHERE to_address.address IS NULL  -- Negative join
      and evt_block_time >= '{{net_flow_start_date}}'

    UNION ALL

    SELECT
      'ethereum'  AS blockchain,
      contract_address AS token_address,
      date_trunc('minute', evt_block_time) AS block_minute,
      value AS amount
    FROM erc20_ethereum.evt_Transfer
      INNER JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
       LEFT JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
    WHERE from_address.address IS NULL  -- Negative join
      and evt_block_time >= '{{net_flow_start_date}}'
  ),

  eth_flow AS (
    SELECT
      'ethereum'  AS blockchain,
      date_trunc('minute', block_time) AS block_minute,
      -value / 1e18                AS amount
    from ethereum.transactions
      INNER JOIN address AS from_address ON from_address.address = transactions.`from`
       LEFT JOIN address AS to_address ON to_address.address == transactions.`to`
    WHERE to_address.address IS NULL  -- Negative join
      AND success
      and block_time >= '{{net_flow_start_date}}'

    UNION ALL

    SELECT
      'ethereum'  AS blockchain,
      date_trunc('minute', block_time) AS block_minute,
      value / 1e18                  AS amount
    from ethereum.transactions
      INNER JOIN address AS to_address ON to_address.address == transactions.`to`
       LEFT JOIN address AS from_address ON from_address.address = transactions.`from`
    WHERE from_address.address IS NULL  -- Negative join
      AND success
      and block_time >= '{{net_flow_start_date}}'
  ),

  price AS (
    SELECT
      date_trunc('minute', minute) AS price_minute,
      contract_address AS token_address,
      decimals,
      symbol,
      avg(price) AS avg_price
    FROM prices.usd
    WHERE blockchain = 'ethereum'
      AND minute >= '{{net_flow_start_date}}'
    GROUP BY 1, 2, 3, 4
  )

  SELECT
    blockchain,
    date_trunc('day', block_minute) AS block_date,
    p.symbol,
    SUM(amount / power(10, p.decimals)) AS amount,
    SUM(amount / power(10, p.decimals) * p.avg_price) AS amount_usd,
    SUM(CASE WHEN amount >= 0 THEN (amount * p.avg_price) / power(10, p.decimals) ELSE 0 END) AS inbound_usd,
    SUM(CASE WHEN amount < 0 THEN (amount * p.avg_price) / power(10, p.decimals) ELSE 0 END) AS outbound_usd
  FROM erc20_token_flow AS erc20
    INNER JOIN price AS p
            ON erc20.token_address = p.token_address
           AND erc20.block_minute = p.price_minute
  WHERE p.token_address is not null
  GROUP BY 1, 2, 3

  UNION ALL

  SELECT
    blockchain,
    date_trunc('day', e.block_minute) AS block_date,
    'ETH' AS symbol,
    SUM(amount) AS amount,
    SUM(amount * avg_price) AS amount_usd,
    SUM(CASE WHEN amount >= 0 THEN amount * p.avg_price ELSE 0 END) AS inbound_usd,
    SUM(CASE WHEN amount < 0 THEN amount * p.avg_price ELSE 0 END) AS outbound_usd
  FROM eth_flow AS e
    INNER JOIN price AS p
            ON e.block_minute = p.price_minute
           AND p.symbol = 'WETH'
  GROUP BY 1, 2, 3
)


SELECT
  block_date,
  symbol,
  SUM(amount_usd) AS total_net_usd,
  SUM(inbound_usd) AS inbound_usd,
  SUM(outbound_usd) AS outbound_usd,
  SUM(CASE WHEN blockchain = 'ethereum' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS ethereum_net_usd,
  SUM(CASE WHEN blockchain = 'polygon' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS polygon_net_usd,
  SUM(CASE WHEN blockchain = 'optimism' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS optimism_net_usd,
  SUM(CASE WHEN blockchain = 'arbitrum' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS arbitrum_net_usd,
  SUM(CASE WHEN blockchain = 'bnb' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS bnb_net_usd,
  SUM(CASE WHEN blockchain = 'avalanche' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS avalanche_net_usd
FROM ethereum_token_flow
WHERE symbol is not null
  and amount is not null
  --and amount not between -1 and 1
group by 1,2
order by 1 desc, 2
