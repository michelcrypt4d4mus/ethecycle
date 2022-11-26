WITH address AS (
  SELECT
    address,
    label
  FROM (
    values
        ('0x72a53cdbbcc1b9efa39c834a540550e23463aacb', 'Crypto.com 1'),
        ('0x46340b20830761efd32832a74d7169b29feb9758', 'Crypto.com 2'),
        ('0xcffad3200574698b78f32232aa9d63eabd290703', 'Crypto.com 3'),
        ('0x7758e507850da48cd47df1fb5f875c23e3340c50', 'Crypto.com 4'),
        ('0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b', 'CRONOS Token'),
        ('0x6262998ced04146fa42253a5c0af90ca02dfd2a3', 'Crypto.com 5'),
        ('0xb63b606ac810a52cca15e44bb630fd42d8d1d83d', 'Crypto.com: MCO Token')
  ) AS t(address, label)
),

txns AS (
  SELECT
    'polygon' AS blockchain,
    contract_address,
    date_trunc('minute', evt_block_time) AS block_minute,
    -value AS amount
  FROM erc20_polygon.evt_Transfer
    INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
     LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
  WHERE to_address.address IS NULL  -- Negative join
    AND evt_block_time >= '{{net_flow_start_date}}'

  UNION ALL

  SELECT
    'polygon' AS blockchain,
    contract_address,
    date_trunc('minute', evt_block_time) AS block_minute,
    value AS amount
  FROM erc20_polygon.evt_Transfer
    INNER JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
     LEFT JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
  WHERE from_address.address IS NULL  -- Negative join
    and evt_block_time >= '{{net_flow_start_date}}'
  LIMIT 1000
),

txn_minutes AS (
    SELECT
      block_minute
    FROM txns
    GROUP BY 1
),

-- Polygon token Prices without USDC
prices_polygon_raw AS (
  SELECT
    COALESCE(blockchain, 'polygon') AS blockchain,
    date_trunc('minute', minute) AS price_minute,
    contract_address,
    decimals,
    symbol,
    avg(price) AS avg_price
  FROM prices.usd
  WHERE (blockchain = 'polygon' OR blockchain IS NULL)
    AND minute >= '{{net_flow_start_date}}'
  GROUP BY 1, 2, 3, 4, 5
),

weth_prices AS (
  SELECT
    'polygon',
    DATE(usd.minute) AS weth_price_date,
    '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619' AS contract_address,
    usd.decimals,
    usd.symbol,
    avg(price) AS avg_price
  FROM prices.usd
    INNER JOIN txn_minutes
            ON txn_minutes.block_minute = usd.minute
  WHERE symbol = 'WETH'
    AND (blockchain = 'ethereum' OR blockchain IS NULL)
  GROUP BY 1,2,3,4,5
),

prices_polygon AS (
  -- Prices on Polygon chain
  SELECT * FROM prices_polygon_raw

  UNION ALL

  -- Add USDC at $1
  SELECT
    'polygon',
    block_minute,
    '0x2791bca1f2de4661ed88a30c99a7a9449aa84174' AS contract_address,
    6 AS decimals,
    'USDC' AS symbol,
    1.0 AS avg_price
  FROM txn_minutes
  GROUP BY 1,2,3,4,5,6
),

txns_with_prices AS (
  SELECT
    txns.blockchain,
    txns.contract_address,
    prices_polygon.symbol,
    block_minute,
    amount AS token_count_raw,
    amount / power(10, prices_polygon.decimals) AS token_count,
    amount / power(10, prices_polygon.decimals) * COALESCE(prices_polygon.avg_price, weth_prices.avg_price) AS amount_usd
  FROM txns
    LEFT JOIN prices_polygon
           ON prices_polygon.contract_address = txns.contract_address
          AND prices_polygon.price_minute = txns.block_minute
          AND prices_polygon.blockchain = txns.blockchain
    LEFT JOIN weth_prices
           ON txns.contract_address = '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619'
          AND weth_prices.weth_price_date = date(block_minute)
)

SELECT
  DATE(block_minute) AS date,
  CASE WHEN symbol IS NULL THEN block_minute ELSE 'KNOWN SYMBOL' END AS block_minute,
  CASE WHEN symbol IS NULL THEN contract_address ELSE 'KNOWN SYMBOL' END AS contract_address,
  SUM(amount_usd) AS total_net_usd,
  SUM(token_count) AS token_count
FROM txns_with_prices
WHERE token_count_raw is not null
  --and amount not between -1 and 1
GROUP BY 1,2,3
ORDER BY 1 DESC,2
