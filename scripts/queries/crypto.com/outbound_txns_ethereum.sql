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

eth_txns AS (
  SELECT
    'ethereum' AS blockchain,
    `from` AS from_address,
    `to` AS to_address,
    NULL AS contract_address,
    date_trunc('minute', block_time) AS block_minute,
    SUM(value / 1e18) AS txn_value,
    COUNT(*) AS txn_count
  FROM ethereum.transactions
    INNER JOIN address AS from_address ON from_address.address = transactions.`from`
     LEFT JOIN address AS to_address ON to_address.address == transactions.`to`
  WHERE success
    AND block_time >= '{{recent_outbound_cutoff_time}}'
    AND to_address.address IS NULL  -- Negative join
  GROUP BY 1,2,3,4,5
),

erc20_txns AS (
  SELECT
    'ethereum' AS blockchain,
    `from` AS from_address,
    `to` AS to_address,
    contract_address,
    DATE_TRUNC('minute', evt_block_time) AS block_minute,
    SUM(value) AS txn_value,
    COUNT(*) AS txn_count
  FROM erc20_ethereum.evt_Transfer
    INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
     LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
  WHERE evt_block_time > '{{recent_outbound_cutoff_time}}'
  GROUP BY 1,2,3,4,5
),

txns AS (
  SELECT * FROM eth_txns
  UNION ALL
  SELECT * FROM erc20_txns
),

prices_by_minute AS (
  SELECT
    date_trunc('minute', minute) AS price_minute,
    contract_address,
    decimals,
    symbol,
    avg(price) AS avg_price
  FROM prices.usd
  WHERE blockchain = 'ethereum'
    AND minute >= '{{recent_outbound_cutoff_time}}'
  GROUP BY 1, 2, 3, 4
)


SELECT
  txns.block_minute AS minute_txn_sent_at,

  CASE
    WHEN usd.contract_address IS NULL THEN
      'eth'
    ELSE
      usd.symbol
    END AS symbol,

  prices_by_minute.avg_price * (txn_value / power(10, prices_by_minute.decimals)) AS amount_usd,
  from_address,
  LEFT(get_labels(from_address), 35) AS from_label_short,
  to_address,
  LEFT(get_labels(to_address), 35) AS to_label_short,
  txn_value / power(10, prices_by_minute.decimals) AS token_count,
  txn_count,
  get_labels(from_address) AS from_labels_full,
  get_labels(to_address) AS to_labels_full
FROM txns
  INNER JOIN prices_by_minute
          ON prices_by_minute.price_minute = txns.block_minute
         AND (
            prices_by_minute.contract_address = txns.contract_address
            OR
            prices_by_minute.contract_address IS NULL AND txns.contract_address IS NULL
         )
WHERE prices_by_minute.avg_price * (txn_value / power(10, prices_by_minute.decimals)) > {{minimum_txn_usd}}
ORDER BY 1 DESC
