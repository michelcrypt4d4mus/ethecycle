-- Aggregate by minute/token/from_address
WITH ftx_inbound AS (
  SELECT
    `from` AS from_address,
    contract_address,
    DATE_TRUNC('minute', evt_block_time) AS minute,
    SUM(value) AS inbound_value,
    COUNT(*) AS inbound_txn_count
  FROM erc20_ethereum.evt_Transfer
  WHERE `to` IN (
      '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2',
      '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94',
      '0x7abe0ce388281d2acf297cb089caef3819b13448'
    )
  GROUP BY 1,2,3
),

-- Convert to USD, aggregate just by from_address
ftx_inbound_usd AS (
  SELECT
    from_address,
    usd.symbol,
    SUM(inbound_txn_count) AS inbound_txn_count,
    SUM(usd.price * inbound_value) / power(10, FIRST(usd.decimals)) AS inbound_usd
  FROM ftx_inbound
    INNER JOIN prices.usd
            ON usd.blockchain = 'ethereum'
           AND usd.contract_address = ftx_inbound.contract_address
           AND usd.minute = ftx_inbound.minute
  GROUP BY 1,2
),

-- Aggregate by minute/token/from_address
ftx_outbound AS (
  SELECT
    `to` AS to_address,
    contract_address,
    DATE_TRUNC('minute', evt_block_time) AS minute,
    SUM(value) AS outbound_value,
    COUNT(*) AS outbound_txn_count
  FROM erc20_ethereum.evt_Transfer
  WHERE `from` IN (
    '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2',
    '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94',
    '0x7abe0ce388281d2acf297cb089caef3819b13448'
  )
  GROUP BY 1,2,3
),

-- Convert to USD, aggregate just by from_address
ftx_outbound_usd AS (
  SELECT
    to_address,
    usd.symbol,
    SUM(outbound_txn_count) AS outbound_txn_count,
    SUM(usd.price * outbound_value) / power(10, FIRST(usd.decimals)) AS outbound_usd
  FROM ftx_outbound
    INNER JOIN prices.usd
            ON usd.blockchain = 'ethereum'
           AND usd.contract_address = ftx_outbound.contract_address
           AND usd.minute = ftx_outbound.minute
    GROUP BY 1,2
)


SELECT
  COALESCE(from_address, to_address) AS wallet_address,
  get_labels(COALESCE(from_address, to_address)) AS labels,
  COALESCE(ftx_inbound_usd.symbol, ftx_outbound_usd.symbol) AS symbol,

  -- Inbound
  ROUND(COALESCE(inbound_usd, 0)) AS inbound_usd,
  COALESCE(inbound_txn_count, 0) AS inbound_txn_count,
  ROUND(COALESCE(inbound_usd, 0) / COALESCE(inbound_txn_count, 1)) AS inbound_avg_usd_per_txn,

  -- Outbound
  ROUND(COALESCE(outbound_usd, 0)) AS outbound_usd,
  COALESCE(outbound_txn_count, 0) AS outbound_txn_count,
  ROUND(COALESCE(outbound_usd, 0) / COALESCE(outbound_txn_count, 1)) AS outbound_avg_usd_per_txn,

  -- Totals
  ROUND(COALESCE(outbound_usd, 0) + COALESCE(inbound_usd, 0)) AS gross_usd_volume
FROM ftx_inbound_usd
  FULL OUTER JOIN ftx_outbound_usd
               ON ftx_outbound_usd.to_address = ftx_inbound_usd.from_address
              AND ftx_inbound_usd.symbol = ftx_outbound_usd.symbol
ORDER BY gross_usd_volume DESC
LIMIT 500
