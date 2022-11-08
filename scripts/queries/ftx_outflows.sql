WITH top_100 AS (
    SELECT
      `to` AS to_address,
      usd.symbol,
      FIRST(usd.price) * SUM(value) / power(10, FIRST(usd.decimals)) AS usd_value,
      COUNT(*) AS txn_count
    FROM erc20_ethereum.evt_Transfer
      JOIN prices.usd
        ON usd.contract_address = evt_Transfer.contract_address
       AND usd.blockchain = 'ethereum'
       AND usd.minute = DATE_TRUNC('minute', evt_block_time)
    WHERE `from` IN (
        '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2',
        '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94',
        '0x7abe0ce388281d2acf297cb089caef3819b13448'
    )
    GROUP BY 1,2
    ORDER BY 3 DESC
    LIMIT 5000
)

SELECT
  get_labels(to_address) AS labels,
  to_address,
  symbol,
  ROUND(usd_value,2) AS usd_value,
  txn_count,
  ROUND(usd_value / txn_count, 2) AS avg_usd_per_txn
FROM top_100
WHERE to_address NOT IN ('0xa00b0540f43e00a634d016a31b0a39d95170e6bf')
ORDER BY 6 DESC
