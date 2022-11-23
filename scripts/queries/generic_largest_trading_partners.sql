-- Aggregate by minute/token/from_address
WITH inbound AS (
  SELECT
    `from` AS from_address,
    contract_address,
    evt_tx_hash AS tx_id,
    DATE_TRUNC('minute', evt_block_time) AS minute,
    SUM(value) AS inbound_value,
    COUNT(*) AS inbound_txn_count
  FROM erc20_ethereum.evt_Transfer
  WHERE evt_block_time > '{{gross_flow_start_time}}'
    AND `to` = '{{ethereum_wallet_address}}'
  GROUP BY 1,2,3,4
),

-- Convert to USD, aggregate just by from_address
inbound_usd AS (
  SELECT
    from_address,
    usd.symbol,
    collect_list(tx_id) AS tx_ids,
    MIN(inbound.minute) AS first_in_txn_at,
    MAX(inbound.minute) AS last_in_txn_at,
    SUM(inbound_txn_count) AS inbound_txn_count,
    SUM(usd.price * inbound_value) / power(10, FIRST(usd.decimals)) AS inbound_usd
  FROM inbound
    INNER JOIN prices.usd
            ON usd.blockchain = 'ethereum'
           AND usd.contract_address = inbound.contract_address
           AND usd.minute = inbound.minute
  GROUP BY 1,2
),

-- Aggregate by minute/token/from_address
outbound AS (
  SELECT
    `to` AS to_address,
    contract_address,
    DATE_TRUNC('minute', evt_block_time) AS minute,
    evt_tx_hash AS tx_id,
    SUM(value) AS outbound_value,
    COUNT(*) AS outbound_txn_count,
    collect_list(evt_tx_hash) AS tx_ids -- aggregate that collects the array of [code]
  FROM erc20_ethereum.evt_Transfer
  WHERE evt_block_time > '{{gross_flow_start_time}}'
    AND `from` = '{{ethereum_wallet_address}}'
  GROUP BY 1,2,3,4
),

-- Convert to USD, aggregate just by from_address
outbound_usd AS (
  SELECT
    outbound.to_address,
    usd.symbol,
    collect_list(tx_id) AS tx_ids,
    MIN(outbound.minute) AS first_out_txn_at,
    MAX(outbound.minute) AS last_out_txn_at,
    SUM(outbound_txn_count) AS outbound_txn_count,
    SUM(usd.price * outbound_value) / power(10, FIRST(usd.decimals)) AS outbound_usd
  FROM outbound
    INNER JOIN prices.usd
            ON usd.blockchain = 'ethereum'
           AND usd.contract_address = outbound.contract_address
           AND usd.minute = outbound.minute
    GROUP BY 1,2
)


SELECT
  COALESCE(from_address, to_address) AS wallet_address,
  get_labels(COALESCE(from_address, to_address)) AS labels,
  COALESCE(inbound_usd.symbol, outbound_usd.symbol) AS symbol,
  ROUND(COALESCE(outbound_usd, 0) + COALESCE(inbound_usd, 0)) AS gross_usd_volume,
  ROUND(COALESCE(inbound_usd, 0) - COALESCE(outbound_usd, 0)) AS net_usd_volume,

  -- Inbound
  ROUND(COALESCE(inbound_usd, 0)) AS inbound_usd,
  COALESCE(inbound_txn_count, 0) AS inbound_txn_count,
  ROUND(COALESCE(inbound_usd, 0) / COALESCE(inbound_txn_count, 1)) AS inbound_avg_usd_per_txn,
  first_in_txn_at,
  last_in_txn_at,

  -- Outbound
  ROUND(COALESCE(outbound_usd, 0)) AS outbound_usd,
  COALESCE(outbound_txn_count, 0) AS outbound_txn_count,
  ROUND(COALESCE(outbound_usd, 0) / COALESCE(outbound_txn_count, 1)) AS outbound_avg_usd_per_txn,
  first_out_txn_at,
  last_out_txn_at,
  LEFT(array_join(outbound_usd.tx_ids, ', '), 1024) AS output_tx_ids,
  LEFT(array_join(inbound_usd.tx_ids, ', '), 1024) AS inbound_tx_ids
FROM inbound_usd
  FULL OUTER JOIN outbound_usd
               ON outbound_usd.to_address = inbound_usd.from_address
              AND inbound_usd.symbol = outbound_usd.symbol
WHERE ROUND(COALESCE(outbound_usd, 0) + COALESCE(inbound_usd, 0)) > {{min_gross_usd_volume}}
ORDER BY gross_usd_volume DESC
LIMIT 500
