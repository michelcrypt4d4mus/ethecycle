WITH prices_by_minute AS (
    SELECT
      usd.contract_address,
      usd.blockchain,
      usd.minute,
      usd.decimals,
      AVG(usd.price) AS price
    FROM prices.usd
    WHERE usd.blockchain = 'ethereum'
    GROUP BY 1,2,3,4
),

ftx_inbound AS (
    SELECT
      `from` AS from_address,
      SUM(prices_by_minute.price * value) / power(10, FIRST(prices_by_minute.decimals)) AS inbound_usd,
      COUNT(*) AS inbound_txn_count
    FROM erc20_ethereum.evt_Transfer
      INNER JOIN prices_by_minute
              ON prices_by_minute.contract_address = evt_Transfer.contract_address
             AND prices_by_minute.minute = DATE_TRUNC('minute', evt_block_time)
    WHERE `to` IN (
        '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2',
        '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94',
        '0x7abe0ce388281d2acf297cb089caef3819b13448'
       )
     GROUP BY 1
     LIMIT 10000
),

ftx_outbound AS (
    SELECT
      `to` AS to_address,
      SUM(prices_by_minute.price * value) / power(10, FIRST(prices_by_minute.decimals)) AS outbound_usd,
      COUNT(*) AS outbound_txn_count
    FROM erc20_ethereum.evt_Transfer
      INNER JOIN prices_by_minute
              ON prices_by_minute.contract_address = evt_Transfer.contract_address
             AND prices_by_minute.minute = DATE_TRUNC('minute', evt_block_time)
    WHERE `from` IN (
        '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2',
        '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94',
        '0x7abe0ce388281d2acf297cb089caef3819b13448'
       )
     GROUP BY 1
     LIMIT 10000
)

SELECT
  COALESCE(from_address, to_address) AS wallet_address,
  get_labels(COALESCE(from_address, to_address)) AS labels,

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
FROM ftx_inbound
  FULL OUTER JOIN ftx_outbound
                ON ftx_outbound.to_address = ftx_inbound.from_address
ORDER BY gross_usd_volume DESC
LIMIT 500
